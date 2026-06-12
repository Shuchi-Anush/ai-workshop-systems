# Retrieval Pipeline

The retrieval pipeline encompasses the flow from a user query (Job Description) to the fetching of relevant candidate chunks.

1. **Query Processing**: The JD is parsed and optionally expanded (e.g., synonym expansion for skills).
2. **Query Embedding**: `IEmbedder` converts the processed JD into a query vector.
3. **Vector Search**: `IVectorDB` performs a nearest-neighbor search (Top-K) using the query vector to return `chunk_ids`.
4. **Metadata Rehydration**: The relational store is queried using the retrieved `chunk_ids` to fetch the actual text, `candidate_id`, and `section` metadata.
5. **Output**: Handed off to the Aggregation and Ranking pipelines.
