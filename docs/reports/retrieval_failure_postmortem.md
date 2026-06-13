# Incident Postmortem: The Adversarial Collapse of Dense RAG

## Incident Summary
During initial baseline benchmarking of the Resume Intelligence platform, a critical vulnerability was exposed. A syntactically meaningless string of 200 technical buzzwords (the `adv_hr_keyword_stuffed` document) successfully manipulated the latent vector space, achieving Rank #1 for 85% of technical queries, effectively overriding highly qualified, legitimate engineering resumes.

## Root Cause Analysis
The failure was traced to a fundamental mathematical behavior of Dense Embeddings (`nomic-embed-text`).
Vector models map documents into a high-dimensional space based on the contextual co-occurrence of tokens. Because the adversarial document contained nearly every relevant technical token across the software engineering domain, its vector representation sat exactly in the mathematical center (the "gravity well") of the engineering cluster. 

When a query was embedded, the cosine distance to this gravity well was naturally shorter than the distance to a legitimate resume, which contained semantic noise (e.g., standard English grammar, soft skills, company descriptions).

### Why LLM Validation Failed
Initially, we attempted to use an LLM (`phi3`) to validate the retrieved documents and discard the fraud. 
**Result:** Complete system stall. Passing 5 resumes into a local 8GB-constrained LLM took >25 seconds, violating the 100ms retrieval SLA. The architectural boundary of "Retrieval" vs "Generation" was breached.

## The Resolution
We treated this not as an AI problem, but as an Information Retrieval (IR) problem.
We implemented **Hybrid Reciprocal Rank Fusion (RRF)**.

1. **The Introduction of BM25:**
   We indexed all documents into a traditional TF-IDF Sparse engine. Because BM25 relies heavily on document length normalization, the massive block of stuffed keywords diluted the BM25 term frequency. The adversarial document ranked terribly in the sparse space.

2. **The Fusion Mathematics:**
   By combining the ranks (`1/(60+Rank)`), the adversarial document's high Dense score was neutralized by its catastrophic Sparse score.

3. **The Heuristic Kill-Switch:**
   To guarantee safety, we introduced an `AdversarialDetector` in the retrieval loop. By applying a fast, deterministic check for Noun-Stacking ratios (via NLP libraries), we applied a `0.1x` penalty multiplier to documents lacking grammatical structure, burying them permanently before the LLM ever saw them.

## Lessons Learned
1. **Never trust raw embeddings.** Dense space is easily manipulated by syntax-agnostic keyword clusters.
2. **LLMs are not firewalls.** Using an LLM to validate search results creates unacceptable operational bottlenecks.
3. **Hybrid is mandatory.** Combining exact-match frequency (BM25) with semantic intent (Vectors) is the only production-safe retrieval architecture.
