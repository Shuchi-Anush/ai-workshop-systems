# Task 01: Resume Analyzer & Ranking System

Welcome to Task 01 of the AI Engineering Workshop! This application demonstrates an end-to-end Retrieval-Augmented Generation (RAG) pipeline for processing and ranking resumes against job descriptions.

## 🌟 Project Overview
The Resume Analyzer ingests PDF resumes, chunks them semantically, embeds them using local models, and stores them in a vector database. It then retrieves the most relevant candidate chunks for a given job description and uses a Large Language Model to score and provide explainable ranking.

## 🏗 Architecture
This app implements the strict platform boundaries defined by the `ai-workshop-systems` monorepo:
* **Backend:** FastAPI, Python 3.11+
* **Vector DB:** ChromaDB (Local Persistence)
* **Metadata Store:** Local JSON (Survives Restarts)
* **LLM:** Ollama `phi3:mini` (Local Execution)
* **Embeddings:** Ollama `nomic-embed-text` (Local Execution)

## 📁 Folder Structure
```text
apps/resume-analyzer/
├── pyproject.toml        # App dependencies
├── data/                 # Resumes, metadata, and ChromaDB storage
├── scripts/              # Dataset loading scripts
├── tests/                # Application specific tests
└── src/apps/resume_analyzer/
    └── backend/
        ├── api/          # FastAPI Routes & Main
        ├── di/           # Dependency Injection & Infrastructure Wiring
        ├── parser/       # PDF Extraction & Cleaning
        ├── rag/          # Embedding, VectorDB & Storage logic
        ├── pipelines/    # High-level orchestration
        └── schemas/      # Pydantic data models
```

## 🛠 Setup & Installation

We use `uv` for lightning-fast dependency management and virtual environments.

1. **Install Dependencies:**
   ```bash
   # From the repository root
   uv sync
   ```
## Local Environment Setup
Before starting the workshop, attendees must ensure they have `uv`, `Ollama`, and `git` installed.

### 1. Start Local LLM
Ensure Ollama is running and pull the necessary models:
```bash
ollama run phi3:mini
ollama pull nomic-embed-text
```

### 2. Install Dependencies
```bash
uv sync
```

### 3. Start the Backend Server
```bash
uv run uvicorn apps.resume_analyzer.backend.api.main:app --port 8081
```

## Workshop Demo Flow
Follow these exact steps to demonstrate the end-to-end functionality of Task 01:

1. **Access Swagger UI:**
   Open http://localhost:8081/docs in your browser.

2. **Verify Empty State:**
   Execute the `GET /stats` endpoint. It should return `0` for chunks and candidates.

3. **Ingest Resumes:**
   Execute the `POST /bulk-ingest` endpoint. Upload the sample PDF resumes provided in `apps/resume-analyzer/data/resumes/`. The system will sequentially embed and index them locally.

4. **Verify Ingestion:**
   Execute `GET /stats` again. The chunk and candidate counts should now be non-zero.

5. **Evaluate Candidates:**
   Execute the `POST /evaluate` endpoint with a sample Job Description.
   Example Request Body:
   ```json
   {
     "job_description": "Looking for a Senior Python Developer with FastAPI and RAG experience.",
     "top_k": 5
   }
   ```
   *The system will return ranked candidates and an explainability log from phi3:mini.*

6. **Reset Database:**
   If you need to restart, execute `POST /reset-db?confirm=true` to wipe the local ChromaDB and metadata persistence.

## 🚀 Running the Application

**Run the Backend (FastAPI):**
```bash
# Navigate to the app folder
cd apps/resume-analyzer

# Start the development server
uv run uvicorn src.apps.resume_analyzer.backend.api.main:app --port 8081 --reload
```

*The API documentation (Swagger UI) will be available at [http://localhost:8081/docs](http://localhost:8081/docs).*

## ⚡ API Walkthrough

### 1. Ingest a Single Resume
```bash
curl -X POST "http://localhost:8081/ingest" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "candidate_id=john_doe" \
  -F "file=@/path/to/resume.pdf"
```

### 2. Bulk Ingest Resumes
Use the Swagger UI or the dataset utility script to ingest multiple resumes.
```bash
uv run python scripts/load_dataset.py --path data/resumes --api-url http://localhost:8081
```

### 3. Evaluate Candidates against a Job Description
```bash
curl -X POST "http://localhost:8081/evaluate" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
        "job_description": "Looking for a Senior Python Developer with FastAPI and RAG experience.",
        "top_k": 5
      }'
```

### 4. Admin & Diagnostic Endpoints
- `GET /stats`: View total indexed candidates and chunks
- `GET /candidates`: View a list of indexed candidate IDs
- `GET /candidate/{id}`: View details for a specific candidate
- `POST /reset-db?confirm=true`: Wipe ChromaDB and metadata

## 🔧 Troubleshooting

- **Server Crash on Boot:** Ensure `uv sync` has run and you are running via `uv run`.
- **Ollama Connection Refused:** Make sure Ollama is running in the background.
- **Empty Embeddings:** Verify `nomic-embed-text` is installed (`ollama list`).
- **Database Corruption:** If the metadata or ChromaDB becomes corrupted, hit `/reset-db?confirm=true` and reingest the dataset.

## 🎓 Workshop Explanation
This application is designed as the "Innovation Sandbox". The underlying interfaces (e.g., `IVectorDB`, `IRanker`) are strictly enforced by the `packages/ai-contracts` module. During the workshop, you can safely experiment inside this folder without breaking the core platform rules.
