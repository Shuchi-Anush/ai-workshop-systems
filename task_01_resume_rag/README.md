# Task 01 — Resume RAG System

Production-oriented Retrieval-Augmented Generation (RAG) pipeline for resume ingestion, embedding, retrieval, candidate ranking, and recruiter-facing semantic matching workflows.

---

## Objective

The system is designed to solve semantic candidate-job matching through:

* Resume parsing
* Text normalization
* Intelligent chunking
* Embedding generation
* Vector retrieval
* Ranking orchestration
* Candidate scoring

The architecture prioritizes modularity, deterministic processing, and production-oriented retrieval workflows.

---

## Current Scope

### Stable

| Component                 | Status |
| ------------------------- | ------ |
| PDF resume parsing        | ✅      |
| DOCX resume parsing       | ✅      |
| Resume cleaning pipeline  | ✅      |
| Embedding generation      | ✅      |
| FAISS vector indexing     | ✅      |
| FastAPI service structure | ✅      |
| Modular project layout    | ✅      |

### In Progress

| Component                 | Status |
| ------------------------- | ------ |
| Candidate ranking weights | 🔄     |
| Hybrid semantic scoring   | 🔄     |
| Metadata-aware retrieval  | 🔄     |
| API orchestration layer   | 🔄     |

### Planned

| Component                 | Status |
| ------------------------- | ------ |
| Recruiter dashboard       | 📋     |
| LLM summarization         | 📋     |
| Redis caching             | 📋     |
| PostgreSQL metadata store | 📋     |
| Async ingestion pipeline  | 📋     |
| Multi-tenant support      | 📋     |

---

## System Architecture

```text
Resume Files
     │
     ▼
Document Parsers
(PDF / DOCX)
     │
     ▼
Text Cleaning Pipeline
     │
     ▼
Chunking Engine
     │
     ▼
Embedding Generator
(Sentence Transformers)
     │
     ▼
FAISS Vector Store
     │
     ▼
Retriever
     │
     ▼
Ranking Engine
     │
     ▼
FastAPI Response Layer
```

---

## Repository Structure

```text
task_01_resume_rag/
│
├── data/
│   ├── resumes/
│   ├── jds/
│   └── vector_db/
│
├── notebooks/                 # Experiments and evaluation
│
├── outputs/                   # Generated outputs
│
├── src/
│   ├── api/                   # FastAPI layer
│   ├── parser/                # PDF and DOCX parsing
│   ├── rag/                   # Chunking, embeddings, retrieval
│   ├── ranking/               # Candidate scoring logic
│   ├── services/              # Business orchestration
│   └── utils/                 # Shared helpers
│
├── tests/
│
├── requirements.txt
└── README.md
```

---

## Core Components

### Parser Layer

Responsible for:

* PDF extraction
* DOCX extraction
* Raw text normalization
* Encoding cleanup

Hard constraints:

* No embedding logic
* No ranking logic
* No retrieval logic

---

### Chunking Layer

Responsible for:

* Context-preserving segmentation
* Token-aware splitting
* Semantic chunk preparation

Design goals:

* Minimize semantic fragmentation
* Maximize retrieval relevance
* Preserve recruiter-readable context

---

### Embedding Layer

Uses Sentence Transformers for semantic vector generation.

Current embedding responsibilities:

* Resume embeddings
* Job description embeddings
* Chunk-level vectorization

Planned future additions:

* Hybrid sparse+dense retrieval
* Cross-encoder reranking
* Domain-specific fine-tuning

---

### Vector Database

Current vector store:

* FAISS

Responsibilities:

* Similarity search
* Top-k retrieval
* Efficient semantic lookup

Future migration candidates:

* Qdrant
* Weaviate
* PostgreSQL pgvector

---

### Ranking Engine

Responsible for:

* Semantic similarity scoring
* Weighted ranking
* Candidate prioritization

Planned ranking signals:

* Skill overlap
* Experience weighting
* Education relevance
* Keyword confidence
* Semantic alignment

---

## FastAPI Layer

The API layer is intentionally thin.

Responsibilities:

* Request validation
* Serialization
* Response contracts

The API layer must never contain:

* embedding logic
* ranking logic
* parsing logic

Business orchestration belongs in the service layer.

---

## Technology Stack

| Component       | Technology            |
| --------------- | --------------------- |
| Backend         | FastAPI               |
| Embeddings      | Sentence Transformers |
| Vector Store    | FAISS                 |
| ML Stack        | Transformers          |
| Data Processing | Pandas / NumPy        |
| Parsing         | PyPDF / python-docx   |
| API Validation  | Pydantic              |

---

## Development Setup

### Create Virtual Environment

```bash
python -m venv venv
```

### Activate Environment

```powershell
venv\Scripts\Activate.ps1
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run FastAPI Server

```bash
uvicorn src.api.main:app --reload
```

---

## Engineering Principles

The system prioritizes:

* Modular AI pipelines
* Explicit layer boundaries
* Reusable retrieval workflows
* Deterministic processing
* Production-oriented backend design
* Extensible orchestration

---

## Future Roadmap

### Retrieval Improvements

* Hybrid search
* Cross-encoder reranking
* Metadata filtering
* Query expansion

### Infrastructure

* Dockerization
* Async task orchestration
* PostgreSQL integration
* Redis caching

### AI Enhancements

* Resume summarization
* Skill extraction
* Recruiter copilots
* Interview intelligence

---

## Current Non-Goals

Currently out of scope:

* Authentication systems
* Multi-user tenancy
* Distributed vector databases
* Fine-tuned custom LLMs
* Frontend dashboard

These will be introduced only after retrieval architecture stabilizes.

---

## License

MIT License
