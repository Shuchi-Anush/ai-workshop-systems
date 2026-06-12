# Observability & Diagnostics

Production AI systems require deep observability to debug "silent failures" like poor retrieval quality or ingestion degradation.

## What Must Be Observable
1. **Ingestion Tracing**: Track a document from upload -> parsing -> chunking -> vector DB. We must know exactly how many chunks a specific resume produced and if any sections failed to parse.
2. **Retrieval Tracing**: For a given query, track the exact query vector generation latency, FAISS lookup latency, and the number of chunks retrieved.
3. **Ranking Explainability**: The ranking engine must output an audit log detailing exactly *why* a candidate received a specific score (e.g., Base Semantic Score: 0.85, Skill Overlap Bonus: +0.05).
4. **Latency Tracking**: Distinct metrics for embedding generation vs vector search vs DB metadata lookup.

## Implementation Strategy
* Use structured JSON logging via libraries like `structlog`.
* Future readiness: Ensure traces can be exported via OpenTelemetry to systems like Datadog, Jaeger, or LangSmith.
