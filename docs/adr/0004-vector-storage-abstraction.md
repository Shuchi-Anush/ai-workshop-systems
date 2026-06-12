# ADR 0004: Vector Storage Abstraction

**Context**: AI Apps rapidly shift vector database vendors (FAISS -> Qdrant -> Pinecone).
**Decision**: Enforce `IVectorDB` interface at the package level (`ai-vector`). Applications must never import vendor-specific SDKs into business logic.
**Tradeoffs**: Requires maintaining wrapper classes, but guarantees future migration safety.
