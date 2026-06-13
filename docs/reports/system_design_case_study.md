# System Design Case Study: Local-First Hybrid Retrieval Platform

## 1. Context & Constraints
The goal of this platform was to build an AI-powered Resume Intelligence system that could accurately retrieve, rank, and explain candidate matches against complex Job Descriptions. 

**Hard Constraints:**
- **Local-First Processing:** Data privacy laws (GDPR, CCPA) strictly prohibit sending candidate PII to third-party cloud APIs (OpenAI, Anthropic). All processing must happen on-device.
- **Hardware Limitations:** The system must run on standard developer laptops (8GB RAM, CPU-bound).
- **Latency SLA:** Search queries must execute in `< 100ms` to provide a real-time UX. Full LLM evaluation passes (which take `> 10s`) cannot be in the critical retrieval path.

## 2. Architectural Tradeoffs

### Vector Database vs Traditional Search
We initially evaluated Elasticsearch for document retrieval. While incredibly powerful, running a JVM-based Elasticsearch cluster violated the 8GB RAM local-first constraint. 
**Decision:** We selected **ChromaDB** for dense embeddings (SQLite-backed, low footprint) and built a custom **BM25 In-Memory Index** using `rank_bm25` (Pickle-backed) to simulate a lightweight hybrid infrastructure.

### The Problem with Dense-Only RAG
Relying solely on `nomic-embed-text` through ChromaDB yielded an unacceptable failure mode: **Vocabulary Ignorance**.
When a query asked for a "React Developer", Dense retrieval would highly rank "Angular Developers" because the concepts live close to each other in latent space. In recruitment, specific tooling is a binary requirement. We needed exact-match boolean capabilities.

### Designing the Hybrid RRF Pipeline
To satisfy the latency SLA while increasing precision, we implemented a dual-dispatch system:
1. **Thread 1:** Queries ChromaDB for semantic intent.
2. **Thread 2:** Queries the BM25 index for exact vocabulary matches.

Instead of trying to normalize distances (which have vastly different mathematical bounds), we used **Reciprocal Rank Fusion (RRF)**:
`RRF_Score = 1 / (60 + Rank_Dense) + 1 / (60 + Rank_Sparse)`

This algorithm operates in `O(n)` time complexity post-retrieval and adds less than `1ms` of overhead, well within the SLA.

## 3. Defense Against Adversaries
During benchmarking, we discovered that resumes explicitly "stuffed" with invisible keywords manipulated the Dense retrieval space.
Instead of passing every resume to an LLM to check for "fraud" (violating the latency SLA), we built a deterministic **Adversarial Heuristic Pipeline**:
- Evaluates Chunk Token Density.
- Evaluates Noun-Stacking ratios.
If an anomaly is detected, a `0.1x` penalty multiplier is applied to the RRF score, burying the candidate instantly.

## 4. Explainability & Observability
Enterprise systems require explainability. We built a non-LLM `ExplainabilityEngine` that traces the exact origin of a document's score.
By comparing the `query_tokens` against the `chunk_tokens` using basic set intersections, we output a deterministic JSON trace outlining exactly which words triggered the BM25 index, and which semantic metadata triggered the Dense index.

## 5. Conclusion
This architecture proves that highly effective, adversarial-resistant AI systems do not require massive cloud budgets or massive LLMs. By combining old-school Information Retrieval algorithms (BM25) with modern vector mathematics (ChromaDB) and strict operational boundaries, we achieved production-grade search quality on consumer hardware.
