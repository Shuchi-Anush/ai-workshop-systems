# AI Workshop Systems: Repository Deep Analysis & Architecture Plan

This document outlines the initial findings, architectural vision, and action plan for the `ai-workshop-systems` monorepo, fulfilling the requirement to deeply inspect the repository before generating implementation code.

## Repository Analysis

The repository is structured as a production-minded AI engineering monorepo rather than a rapid prototype. It prioritizes explicit boundaries and modularity. 

**Strengths:**
* **Modular Layout**: The split between `shared/` infrastructure and task-specific logic (e.g., `task_01_resume_rag/`) encourages reusability and isolated testing.
* **Separation of Concerns**: The existence of `api`, `parser`, `rag`, `ranking`, and `services` layers within `task_01_resume_rag/src/` demonstrates a mature backend structure.
* **Architecture-First Mindset**: The README establishes clear boundaries (e.g., API layer contains no business logic).

**Current Gaps:**
* **Documentation**: The `docs/` folder exists but lacks the detailed architectural documentation necessary for a production system.
* **Metadata Infrastructure**: While the philosophy emphasizes rich metadata, the current FAISS implementation and schema definitions likely need expansion to support complex section-based chunking and retrieval.
* **Async & Scaling Prep**: No clear scaffolding for async task queues (e.g., Celery, Redis RQ) exists yet, which will be necessary for large-scale document ingestion.

## Inferred Architecture

Based on the repository structure and objectives, the architecture is designed as a **Multi-Stage Semantic Intelligence Pipeline**:

1.  **Ingestion & Parsing (`parser/`)**: Deterministic extraction of raw text from PDFs/DOCXs, preserving semantic blocks (Experience, Education, Skills) rather than naive character splitting.
2.  **Semantic Chunking (`rag/chunker.py`)**: A context-aware chunking strategy that maps structured resume sections to individual vector representations, maintaining rich metadata links back to the candidate and resume.
3.  **Vectorization (`rag/embedder.py`, `rag/vectordb.py`)**: Generation of dense embeddings (via Sentence Transformers) stored in FAISS (with an explicitly planned migration path to Qdrant/PostgreSQL pgvector).
4.  **Retrieval (`rag/retriever.py`)**: Metadata-aware fetching of candidate chunks based on Job Description (JD) semantics.
5.  **Aggregation & Ranking (`ranking/`)**: A crucial step separating this from standard RAG. Chunk-level hits are aggregated to candidate-level scores using weighted heuristics (skills overlap, experience relevance).
6.  **Service Orchestration (`services/`)**: Business logic tying the pipeline together, independent of the FastAPI routing layer.
7.  **API Layer (`api/`)**: Thin Pydantic-validated REST endpoints.

## Missing Systems

To meet the production-oriented and future scaling requirements, the following systems and conceptual frameworks are currently missing or under-developed:

*   **Metadata Management Layer**: A structured database (e.g., PostgreSQL) to hold relational candidate data (Candidate ID -> Resume ID -> Chunk IDs) alongside the vector store.
*   **Asynchronous Ingestion Queue**: A system to handle time-consuming PDF parsing and embedding without blocking API requests.
*   **Structured Chunking Strategy**: The logic to intelligently slice resumes by semantic headers rather than fixed token lengths.
*   **Hybrid Search Mechanisms**: Support for BM25 (sparse) + Dense embeddings, followed by cross-encoder reranking.

## Documentation Generation Plan

Before any core python code is modified, the following documentation will be generated to codify the architectural rules.

### 1. Architecture Docs (`docs/architecture/`)
*   **`system-overview.md`**: High-level component interaction and module boundaries.
*   **`retrieval-pipeline.md`**: Detailed workflow from JD to Chunk retrieval, emphasizing metadata preservation.
*   **`ranking-pipeline.md`**: Candidate aggregation logic and heuristic weighting strategy.
*   **`ingestion-pipeline.md`**: Deterministic parsing and semantic chunking rules.
*   **`vector-storage.md`**: Current FAISS usage and the abstraction contract required.

### 2. Workflow Docs (`docs/workflows/`)
*   **`agy_system_prompt.md`**: Updating with AI context and engineering constraints.
*   **`implementation_strategy.md`**: Phased rollouts and coding standards.
*   **`repository_conventions.md`**: Git flows, testing mandates, and typing requirements.
*   **`development_workflow.md`**: Local environment setup and deterministic testing.

### 3. Task Docs (`docs/tasks/`)
*   **`task_01_resume_rag.md`**: Deep dive into the current Resume RAG specific architecture.

### 4. Future Docs (`docs/future/`)
*   **`qdrant-migration-plan.md`**: Steps to replace FAISS with Qdrant.
*   **`async-ingestion-roadmap.md`**: Plan for introducing Redis/Celery.
*   **`scaling-considerations.md`**: Multi-tenant and distributed retrieval prep.

## Implementation Sequencing Recommendations

Once the documentation is established and approved, the engineering effort should proceed in this order:

1.  **Phase 1: Solidify Data Models (Schemas)**
    *   Define strict Pydantic models in `shared/schemas/` for `DocumentChunk`, `CandidateMetadata`, and `RetrievalResult`.
2.  **Phase 2: Implement Semantic Chunker**
    *   Build out `task_01_resume_rag/src/rag/chunker.py` to support section-aware splitting, discarding naive recursive character splitters.
3.  **Phase 3: VectorDB Abstraction**
    *   Refactor `vectordb.py` to ensure the interface allows an easy swap from FAISS to Qdrant, strictly enforcing metadata insertion.
4.  **Phase 4: Candidate Aggregation & Ranking**
    *   Implement the logic in `ranking/` to aggregate chunk-level hits into candidate-level scores.
5.  **Phase 5: Service Orchestration & API integration**
    *   Wire the completed modules into `resume_service.py` and `candidate_service.py`, exposing them through the FastAPI routes.

---

## User Review Required
> [!IMPORTANT]
> Please review the analysis, missing systems, and documentation generation plan. Upon your approval, I will autonomously generate and populate all missing documentation files across the `docs/` directories. No application code will be generated until the documentation phase is complete.
