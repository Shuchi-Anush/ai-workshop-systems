# Qdrant Migration Plan

Currently, the system uses FAISS. To scale to millions of vectors and utilize payload filtering, we will migrate to Qdrant.

**Steps**:
1. Ensure the `IVectorDB` interface is strictly adhered to. No FAISS imports should exist outside `rag/vectordb_faiss.py`.
2. Provision a local Qdrant container via Docker Compose.
3. Create `rag/vectordb_qdrant.py` implementing `IVectorDB`.
4. Update the dependency injection in `services/resume_service.py` to use the Qdrant implementation.
5. Backfill historical data via a one-off migration script using the `IIngestionService`.
