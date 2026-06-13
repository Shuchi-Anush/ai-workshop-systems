# Task 01: Resume Analyzer & Ranking System

Welcome to Task 01 of the AI Engineering Workshop! This application demonstrates an end-to-end Retrieval-Augmented Generation (RAG) pipeline for processing and ranking resumes against job descriptions.

## 🌟 Project Overview
The Resume Analyzer ingests PDF resumes, chunks them semantically, embeds them using local models, and stores them in a vector database. It then retrieves the most relevant candidate chunks for a given job description and uses a Large Language Model to score and provide explainable ranking.

## 🏗 Architecture
This app implements the strict platform boundaries defined by the `ai-workshop-systems` monorepo:
* **Frontend:** (If applicable, Next.js / React)
* **Backend:** FastAPI, Python 3.11+
* **Vector DB:** ChromaDB (Local Persistence)
* **LLM & Embeddings:** Ollama (Local Execution)

## 📁 Folder Structure
```text
apps/resume-analyzer/
├── pyproject.toml        # App dependencies
├── tests/                # Application specific tests
└── src/apps/resume_analyzer/
    └── backend/
        ├── api/          # FastAPI Routes & Main
        ├── di/           # Dependency Injection & Infrastructure Wiring
        ├── parser/       # PDF Extraction & Cleaning
        ├── rag/          # Embedding, VectorDB & Retrieval logic
        ├── pipelines/    # High-level orchestration (Ingestion & Retrieval)
        └── schemas/      # Pydantic data models
```

## 🛠 Setup & Installation

We use `uv` for lightning-fast dependency management and virtual environments.

1. **Install Dependencies:**
   ```bash
   # From the repository root
   uv sync
   ```

2. **Ollama Setup (Local Inference):**
   Download and install Ollama from [ollama.com](https://ollama.com).
   Pull the required local models:
   ```bash
   ollama pull llama3
   ```

3. **Environment Variables:**
   Create a `.env` file in this directory (or root) if you plan to extend functionality:
   ```env
   # No external API keys needed for the default local setup!
   OLLAMA_MODEL=llama3
   CHROMA_PERSIST_DIR=./chroma_db
   ```

## 🚀 Running the Application

**Run the Backend (FastAPI):**
```bash
# Navigate to the app folder
cd apps/resume-analyzer

# Start the development server
uv run uvicorn src.apps.resume_analyzer.backend.api.main:app --port 8000 --reload
```

*The API documentation (Swagger UI) will be available at [http://localhost:8000/docs](http://localhost:8000/docs).*

**Run the Tests:**
```bash
uv run pytest tests/
```

## 🐳 Docker Usage
To run the production-ready containerized version:
```bash
# From the repository root
docker-compose up --build
```
This automatically mounts models and handles isolated execution.

## ⚡ Example API Requests

### 1. Ingest a Resume
```bash
curl -X POST "http://localhost:8000/ingest" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "candidate_id=john_doe" \
  -F "file=@/path/to/resume.pdf"
```

### 2. Rank Candidates against a Job Description
```bash
curl -X POST "http://localhost:8000/rank" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
        "job_description": "Looking for a Senior Python Developer with RAG and LLM experience.",
        "chunks": []
      }'
```

*(Note: The actual `rank` endpoint expects `chunks` to be passed or relies on a full retrieval pipeline endpoint which integrates retrieval + ranking)*

## 🎓 Workshop Explanation
This application is designed as the "Innovation Sandbox". The underlying interfaces (e.g., `IVectorDB`, `IRanker`) are strictly enforced by the `packages/ai-contracts` module. During the workshop, you can safely experiment inside this folder without breaking the core platform rules.
