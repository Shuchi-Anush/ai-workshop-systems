# Interface Contracts

To ensure interchangeability and prevent tight coupling, the following interfaces must be adhered to across the repository. 

## 1. Parser Interface (`IParser`)
* **Responsibilities**: Extract raw text and structural metadata from documents.
* **Inputs**: Raw byte stream or file path.
* **Outputs**: `ParsedDocument` object containing normalized text and structural markers.
* **Failure Expectations**: Raise specific `ParsingError` for unsupported formats or corrupt files.

## 2. Cleaner Interface (`ICleaner`)
* **Responsibilities**: Normalize text encoding, remove artifacts, and standardize formatting.
* **Inputs**: `ParsedDocument`.
* **Outputs**: Cleaned `ParsedDocument`.

## 3. Section Parser Interface (`ISectionParser`)
* **Responsibilities**: Identify and tag semantic sections (e.g., Experience, Education, Skills).
* **Inputs**: Cleaned `ParsedDocument`.
* **Outputs**: List of `SemanticSection` objects.

## 4. Chunker Interface (`IChunker`)
* **Responsibilities**: Divide sections into semantic chunks suitable for embedding.
* **Inputs**: List of `SemanticSection` objects.
* **Outputs**: List of `DocumentChunk` objects (must include chunk-level metadata).

## 5. Embedder Interface (`IEmbedder`)
* **Responsibilities**: Convert text chunks into dense vector representations.
* **Inputs**: List of strings or `DocumentChunk` objects.
* **Outputs**: List of dense vectors (e.g., `numpy.ndarray` or `list[float]`).
* **Async-Readiness**: Must support batching and potentially async execution for GPU offloading.

## 6. VectorDB Interface (`IVectorDB`)
* **Responsibilities**: Store vectors, persist indexes, and execute similarity searches.
* **Inputs**: Vectors and associated Chunk IDs.
* **Outputs**: List of `VectorSearchResult` objects (Chunk IDs + similarity scores).
* **Migration Constraints**: Must not leak FAISS-specific or Qdrant-specific objects into the Service layer.

## 7. Retriever Interface (`IRetriever`)
* **Responsibilities**: Coordinate vector search and fetch corresponding metadata from the relational store.
* **Inputs**: Job Description (JD) query, filters.
* **Outputs**: List of enriched `RetrievedChunk` objects.

## 8. Candidate Aggregator Interface (`ICandidateAggregator`)
* **Responsibilities**: Group retrieved chunks by Candidate ID.
* **Inputs**: List of `RetrievedChunk` objects.
* **Outputs**: List of `AggregatedCandidate` objects.

## 9. Ranking Interface (`IRanker`)
* **Responsibilities**: Score and sort aggregated candidates based on heuristics.
* **Inputs**: List of `AggregatedCandidate` objects, JD context.
* **Outputs**: Sorted list of `RankedCandidate` objects.

## 10. Ingestion Service Interface (`IIngestionService`)
* **Responsibilities**: Orchestrate the flow from upload to storage.
* **Inputs**: Raw document, Candidate ID.
* **Outputs**: `IngestionResult` (Success status, indexed chunk count).
* **Async-Readiness**: Must be designed to run as a background task (e.g., Celery worker).
