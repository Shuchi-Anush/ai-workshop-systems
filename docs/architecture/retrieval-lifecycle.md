# Retrieval Lifecycle Documentation

This document describes the complete lifecycle from document upload to recruiter-facing output in the `task_01_resume_rag` system.

## 1. Resume Upload & Raw Storage
* **Purpose**: Securely receive and durably store the original file.
* **Inputs**: PDF/DOCX file stream, `candidate_id`.
* **Outputs**: `file_path` or blob storage URI.
* **Persistence**: Raw files must be retained for auditing and re-parsing.

## 2. Parsing & Normalization
* **Purpose**: Extract clean, UTF-8 text free of layout artifacts.
* **Inputs**: File path.
* **Outputs**: Cleaned text string.
* **Failure Modes**: Corrupt files, password-protected PDFs.

## 3. Section Extraction
* **Purpose**: Identify boundaries for Experience, Education, Skills, etc.
* **Inputs**: Cleaned text.
* **Outputs**: Annotated text blocks with section tags.

## 4. Semantic Chunking
* **Purpose**: Divide text into embeddable units without breaking semantic meaning.
* **Inputs**: Annotated text blocks.
* **Outputs**: `DocumentChunk` objects.
* **Metadata Produced**: `chunk_id`, `candidate_id`, `section`, `parent_chunk_id`.

## 5. Embedding Generation
* **Purpose**: Generate dense vectors representing the semantic meaning of each chunk.
* **Inputs**: Chunk text.
* **Outputs**: 768-d or 384-d float arrays.

## 6. Vector Indexing & Metadata Enrichment
* **Purpose**: Store vectors for fast similarity search and metadata for filtering/aggregation.
* **Architecture Note**: Vector storage (FAISS/Qdrant) and Metadata storage (PostgreSQL) are distinctly separated.
* **Inputs**: Vectors, `DocumentChunk` objects.

## 7. Retrieval
* **Purpose**: Find relevant chunks based on a semantic query (Job Description).
* **Inputs**: JD text, `top_k`, filters.
* **Outputs**: Chunk IDs and similarity scores.

## 8. Candidate Aggregation
* **Purpose**: Transition from chunk-level hits to candidate-level entities.
* **Inputs**: Retrieved Chunk IDs.
* **Outputs**: Grouped chunks mapped to `candidate_id`.

## 9. Ranking
* **Purpose**: Apply business heuristics (e.g., years of experience weight) to score candidates.
* **Inputs**: Aggregated candidates.
* **Outputs**: Final sorted list of `RankedCandidate` objects.

## 10. Recruiter-Facing Output
* **Purpose**: Present results via the API layer.
* **Outputs**: JSON response containing candidate profiles, scores, and exact matched chunk text to provide explainability.
