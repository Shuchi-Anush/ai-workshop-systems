# Vector Storage vs Metadata Storage

A core architectural principle of this repository is the strict separation of dense vector storage and relational metadata storage.

## 1. Vector Storage Responsibilities
* **Tool**: Currently FAISS (local). Future: Qdrant or Milvus.
* **Scope**: Storing only the dense vector representation of a chunk and a single unique identifier (`chunk_id`).
* **Why FAISS?**: Ideal for local development, fast prototyping, and running deterministic tests without external infrastructure.
* **Constraints**: FAISS will NOT store complex JSON metadata or candidate relationships.

## 2. Relational Metadata Responsibilities
* **Tool**: Currently in-memory / JSON. Future: PostgreSQL.
* **Scope**: Storing all relationships: Candidate -> Resume -> Chunk. Storing chunk text, section tags, skills arrays, and ingestion timestamps.
* **Why PostgreSQL?**: Metadata filtering (e.g., "only candidates with >5 years experience") is highly inefficient in basic vector stores. Postgres allows complex pre-filtering before or after vector retrieval.

## Future Migration: Qdrant / pgvector
* The `IVectorDB` interface isolates the rest of the application from FAISS. 
* When migrating to Qdrant, we can leverage Qdrant's payload filtering to combine vector search and metadata filtering in one step, OR move completely to PostgreSQL with `pgvector` for unified storage. The interface contracts guarantee this swap will not break the Service or Aggregation layers.
