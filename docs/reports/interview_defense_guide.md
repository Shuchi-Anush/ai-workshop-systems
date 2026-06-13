# Interview Defense Guide: Senior AI Systems Architecture

This guide prepares the operator for defending the technical decisions of this repository during Staff-level System Design interviews.

## 1. "Why didn't you just use LangChain / LlamaIndex?"
**The Trap:** Probing for framework dependency vs first-principles engineering.
**The Defense:** "Frameworks like LangChain are excellent for prototyping, but they introduce massive layers of opaque abstraction and bloated dependency trees. For a platform strictly bound to 8GB local memory, importing heavy frameworks breaks deterministic control over the execution graph. I needed microsecond control over the Reciprocal Rank Fusion loop and explicit access to the ChromaDB query layer to inject custom adversarial heuristics. Building the pipeline natively using FastAPI allowed me to guarantee `<50ms` latency without framework overhead."

## 2. "Why hybrid search instead of just a better embedding model?"
**The Trap:** Testing understanding of information retrieval limitations.
**The Defense:** "No matter how good an embedding model is, Dense Retrieval fundamentally operates on semantic co-occurrence, not exact string matching. If I search for 'FastAPI', a dense model will confidently return 'Flask' or 'Django' because they live in the same latent cluster. BM25 (Sparse) solves the *Vocabulary Mismatch* problem by enforcing term frequency constraints. Hybrid RRF leverages the best of both: Dense for semantic understanding, Sparse for boolean-like exact matching."

## 3. "How did you scale the adversarial defense without LLM latency?"
**The Trap:** Probing for operational pragmatism vs AI idealism.
**The Defense:** "The naive approach to finding keyword stuffers is passing every document to an LLM and asking, 'Is this a real resume?' This takes 20+ seconds and destroys the UX. Instead, I treated it as an Information Retrieval anomaly. The `AdversarialDetector` heuristic uses simple NLP chunking to count the ratio of technical nouns to functional verbs (Noun-Stacking). If a chunk has zero grammatical structure and is purely a block of keywords, it applies a `0.1x` penalty multiplier to the RRF score. This deterministic check executes in <1ms."

## 4. "How do you defend your Monorepo setup over Microservices?"
**The Trap:** Testing for over-engineering (Enterprise Theater).
**The Defense:** "Microservices solve organizational scaling problems, not technical ones. For a system designed for offline execution on a single machine, network hops between Docker containers add unnecessary latency, serialization overhead, and extreme setup friction. A local-first `uv` workspace monorepo ensures that dependencies are globally resolved in under a second while maintaining strict logical boundaries between `packages/` (interfaces) and `apps/` (implementations) via explicit namespace encapsulation."

## 5. "What breaks when this scales to 1,000,000 resumes?"
**The Trap:** Testing for honesty regarding system limitations.
**The Defense:** 
"1. **BM25 In-Memory Scaling:** The current `rank_bm25` implementation holds the entire corpus in memory as a Python object. At 1M records, this will OOM crash. We would need to migrate the Sparse index to a persisted disk-backed engine like Tantivy or Elasticsearch.
 2. **ChromaDB Local Scaling:** Chroma's SQLite backend is highly optimized, but running single-threaded vector scans on 1M records will exceed the 100ms SLA. We'd migrate to a sharded Qdrant or Milvus cluster.
 3. **Ollama Throughput:** Single-threaded local generation limits throughput to ~1 request per second. We'd need to batch inferences or move to vLLM on dedicated GPU hardware."
