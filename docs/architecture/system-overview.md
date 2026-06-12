# System Overview

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
