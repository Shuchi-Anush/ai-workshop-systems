import os
from pathlib import Path

docs_dir = Path("d:/ai-workshop-systems/docs")

files_content = {
    "architecture/system-overview.md": """# System Overview

## Purpose
This document provides a high-level overview of the `ai-workshop-systems` monorepo. The repository is a production-oriented AI engineering environment for building modular systems such as RAG pipelines, semantic search, and candidate intelligence platforms.

## Core Architecture Principles
1. **Interface-First Design**: Components communicate via explicit contracts, allowing underlying implementations (e.g., FAISS to Qdrant) to be swapped without affecting business logic.
2. **Separation of Concerns**: Ingestion, chunking, embedding, vector storage, relational metadata storage, retrieval, aggregation, and ranking are isolated responsibilities.
3. **Deterministic Processing**: Pipelines must produce reproducible outputs, especially during parsing and chunking.
4. **Metadata Primacy**: Rich metadata links chunks to their source candidates/resumes, enabling complex aggregation and filtering.

## Module Boundaries
* **API (`api/`)**: Thin FastAPI routing layer. Strictly handles HTTP requests, validation (Pydantic), and responses. No business logic.
* **Services (`services/`)**: Orchestrates business workflows across multiple specialized modules.
* **Retrieval & Embedding (`rag/`)**: Handles vector generation, index management, and similarity search.
* **Ranking (`ranking/`)**: Aggregates chunk-level hits into candidate-level scores using weighted heuristics.
* **Parsing (`parser/`)**: Deterministically extracts text and semantic structures from documents.
* **Shared (`shared/`)**: Reusable infrastructure, common Pydantic schemas, and utility wrappers.
""",

    "architecture/interface-contracts.md": """# Interface Contracts

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
""",

    "architecture/retrieval-lifecycle.md": """# Retrieval Lifecycle Documentation

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
""",

    "architecture/vector-storage.md": """# Vector Storage vs Metadata Storage

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
""",

    "architecture/evaluation-framework.md": """# Retrieval Evaluation Framework

To transition from prototype to production, retrieval quality must be measurable. This framework defines the offline evaluation strategy.

## Evaluation Dataset Strategy
* We must curate a golden dataset of (Job Description, Candidate Resumes, Relevance Judgments).
* Relevance Judgments will be binary (Relevant / Not Relevant) or graded (0-3 scale).

## Benchmark Methodology
* **Offline Evaluation Workflows**: CI/CD pipelines will run an evaluation suite whenever embedding models, chunking strategies, or ranking heuristics are modified.
* **Metrics**:
  * **Retrieval Metrics (Chunk Level)**: Recall@K, Mean Reciprocal Rank (MRR).
  * **Ranking Metrics (Candidate Level)**: nDCG (Normalized Discounted Cumulative Gain), Precision@K.

## Automation
* The system will include a dedicated `scripts/evaluate_retrieval.py` tool.
* Embedding comparisons (e.g., testing `all-MiniLM-L6-v2` against `bge-large-en`) must be completely automated using the interface contracts.
""",

    "architecture/observability.md": """# Observability & Diagnostics

Production AI systems require deep observability to debug "silent failures" like poor retrieval quality or ingestion degradation.

## What Must Be Observable
1. **Ingestion Tracing**: Track a document from upload -> parsing -> chunking -> vector DB. We must know exactly how many chunks a specific resume produced and if any sections failed to parse.
2. **Retrieval Tracing**: For a given query, track the exact query vector generation latency, FAISS lookup latency, and the number of chunks retrieved.
3. **Ranking Explainability**: The ranking engine must output an audit log detailing exactly *why* a candidate received a specific score (e.g., Base Semantic Score: 0.85, Skill Overlap Bonus: +0.05).
4. **Latency Tracking**: Distinct metrics for embedding generation vs vector search vs DB metadata lookup.

## Implementation Strategy
* Use structured JSON logging via libraries like `structlog`.
* Future readiness: Ensure traces can be exported via OpenTelemetry to systems like Datadog, Jaeger, or LangSmith.
""",

    "architecture/retrieval-pipeline.md": """# Retrieval Pipeline

The retrieval pipeline encompasses the flow from a user query (Job Description) to the fetching of relevant candidate chunks.

1. **Query Processing**: The JD is parsed and optionally expanded (e.g., synonym expansion for skills).
2. **Query Embedding**: `IEmbedder` converts the processed JD into a query vector.
3. **Vector Search**: `IVectorDB` performs a nearest-neighbor search (Top-K) using the query vector to return `chunk_ids`.
4. **Metadata Rehydration**: The relational store is queried using the retrieved `chunk_ids` to fetch the actual text, `candidate_id`, and `section` metadata.
5. **Output**: Handed off to the Aggregation and Ranking pipelines.
""",

    "architecture/ranking-pipeline.md": """# Ranking Pipeline

Unlike standard document QA, Resume RAG requires candidate-level synthesis.

1. **Aggregation**: The `ICandidateAggregator` groups the disparate retrieved chunks by `candidate_id`.
2. **Heuristic Scoring (`IRanker`)**: 
   * A candidate's base score is derived from the aggregated vector similarity scores of their matched chunks.
   * Modifiers are applied based on metadata (e.g., matched chunks in "Experience" section weigh more than "Hobbies").
3. **Sorting**: Candidates are ranked descending by final score.
""",

    "architecture/ingestion-pipeline.md": """# Ingestion Pipeline

The ingestion pipeline must be highly deterministic to ensure predictable chunk generation.

1. **Parsing**: PDF/DOCX -> Raw Text.
2. **Sectioning**: Rule-based or LLM-assisted identification of structural headers.
3. **Chunking**: Sections are split into `DocumentChunk`s. A chunk must NEVER span across two different semantic sections.
4. **Vectorization**: Batched embedding generation.
5. **Storage**: Simultaneous write to Vector DB (FAISS) and Relational DB (Postgres/Mock). Atomic transactions should be simulated or implemented to prevent orphaned vectors.
""",

    "workflows/agy_system_prompt.md": """# AI Engineering System Prompt Configuration

**Role**: You are a senior AI systems engineer inside the `ai-workshop-systems` monorepo.

**Primary Directives**:
1. Prioritize interface-first architecture and modularity.
2. Ensure strict separation between vector storage, metadata storage, and business logic.
3. Generate production-oriented, statically typed Python code (Pydantic).
4. Maintain deterministic behavior in parsing and chunking.
5. Consider observability and future async scalability in all designs.
6. Never split resume sections arbitrarily during chunking.
""",

    "workflows/implementation_strategy.md": """# Implementation Strategy

1. **Define Core Schemas**: Establish Pydantic models in `shared/schemas` for standard data structures.
2. **Define Interfaces**: Create abstract base classes (ABCs) matching the Interface Contracts.
3. **Implement Storage Mocks**: Build in-memory implementations of the VectorDB and Metadata stores for testing.
4. **Build RAG Core**: Implement concrete Chunker, Embedder, and Retriever modules.
5. **Implement Aggregation & Ranking**: Build the candidate grouping logic.
6. **Service & API**: Expose the pipeline via FastAPI.
""",

    "workflows/repository_conventions.md": """# Repository Conventions

* **Typing**: Strict type hints required for all Python code.
* **Validation**: Pydantic models required for all data boundaries.
* **Dependencies**: Managed via standard `requirements.txt` with locked versions. `shared/` dependencies must be kept minimal.
* **Testing**: `pytest` mandatory. Unit tests must use mock VectorDB and Embedders to run offline and deterministically.
""",

    "workflows/development_workflow.md": """# Development Workflow

* **Virtual Environment**: Use `python -m venv venv`.
* **Environment Variables**: Managed via `.env` based on `.env.example`.
* **Execution**: Run API locally via `uvicorn task_01_resume_rag.src.api.main:app --reload`.
* **Iterative Testing**: Use Jupyter notebooks in `task_01_resume_rag/notebooks/` for rapid prototyping of chunking and embedding logic before migrating to `src/`.
""",

    "tasks/task_01_resume_rag.md": """# Task 01: Resume RAG Pipeline

**Status**: Architecture Stabilization Phase.

**Overview**: A specialized Retrieval-Augmented Generation system designed for semantic candidate-job matching.

**Key Differentiators from Standard RAG**:
* Semantic chunking over naive character splitting.
* Candidate-level aggregation post-retrieval.
* Heuristic ranking applied on top of vector similarity.

**Current Focus**: Formalizing interface boundaries and establishing deterministic ingestion.
""",

    "future/qdrant-migration-plan.md": """# Qdrant Migration Plan

Currently, the system uses FAISS. To scale to millions of vectors and utilize payload filtering, we will migrate to Qdrant.

**Steps**:
1. Ensure the `IVectorDB` interface is strictly adhered to. No FAISS imports should exist outside `rag/vectordb_faiss.py`.
2. Provision a local Qdrant container via Docker Compose.
3. Create `rag/vectordb_qdrant.py` implementing `IVectorDB`.
4. Update the dependency injection in `services/resume_service.py` to use the Qdrant implementation.
5. Backfill historical data via a one-off migration script using the `IIngestionService`.
""",

    "future/async-ingestion-roadmap.md": """# Async Ingestion Roadmap

Parsing PDFs and generating embeddings are CPU/GPU bound tasks that will timeout standard HTTP requests.

**Plan**:
1. Introduce Celery + Redis as a task queue.
2. Refactor `IIngestionService` to enqueue tasks rather than process synchronously.
3. API endpoints will return a `task_id` and a `202 Accepted` status.
4. Implement a polling endpoint or webhook callback to notify the client when a candidate's resume has been fully indexed.
""",

    "future/scaling-considerations.md": """# Scaling Considerations

As the system grows, several bottlenecks must be addressed:

1. **Embedding Throughput**: Local Sentence Transformers will bottleneck. Consider deploying a dedicated Triton Inference Server or using managed APIs (e.g., Cohere/OpenAI) if data privacy allows.
2. **Metadata Queries**: As the Postgres database grows, ensure indexes exist on `candidate_id` and `skills` arrays.
3. **Multi-Tenancy**: To support multiple corporate clients, `tenant_id` must be introduced to the `IVectorDB` partition logic (e.g., Qdrant collections/payloads) and all Relational Metadata schemas.
"""
}

# Ensure directories exist
for path_str in files_content.keys():
    full_path = docs_dir / path_str
    full_path.parent.mkdir(parents=True, exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(files_content[path_str])

print(f"Successfully generated {len(files_content)} architecture documents.")
