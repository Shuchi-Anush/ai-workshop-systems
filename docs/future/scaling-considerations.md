# Scaling Considerations

As the system grows, several bottlenecks must be addressed:

1. **Embedding Throughput**: Local Sentence Transformers will bottleneck. Consider deploying a dedicated Triton Inference Server or using managed APIs (e.g., Cohere/OpenAI) if data privacy allows.
2. **Metadata Queries**: As the Postgres database grows, ensure indexes exist on `candidate_id` and `skills` arrays.
3. **Multi-Tenancy**: To support multiple corporate clients, `tenant_id` must be introduced to the `IVectorDB` partition logic (e.g., Qdrant collections/payloads) and all Relational Metadata schemas.
