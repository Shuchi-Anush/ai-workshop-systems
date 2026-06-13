# AI Workshop Systems Monorepo

Welcome to the AI Engineering Workshop. This repository is a Dual-Zone Monorepo designed to support rapid prototyping of AI applications while maintaining production-grade architectural boundaries.

## Core Objectives

This workspace exists to support:
* Retrieval-Augmented Generation (RAG) systems
* FastAPI-based AI services
* Local LLM orchestration (Ollama)
* Vector search pipelines (ChromaDB)
* Resume intelligence systems
* AI engineering experimentation

The focus is not rapid prototyping alone, but engineering maintainable, extensible, and operationally structured AI systems.

---

## Repository Philosophy (Dual-Zone Strategy)

The monorepo strictly enforces a Dual-Zone Architecture:

1. **`packages/` (Frozen Platform Infrastructure)**
   - Contains highly reusable, robust interfaces and implementations.
   - Example: `ai-contracts` defines the rules for how vector DBs, embedders, and parsers must behave.
   - NEVER import from `apps/` into `packages/`.

2. **`apps/` (Innovation Zone)**
   - Contains isolated workshop tasks and standalone applications.
   - Example: `apps/resume-analyzer` is the Task 01 application.
   - Safe to hack, experiment, and mutate during the workshop.
   - NEVER import from `apps/` into another `apps/`.

---

## Current Tasks

| Task | App Folder | Description | Status |
| --- | --- | --- | --- |
| `Task 01` | `apps/resume-analyzer` | Resume parsing, embedding, retrieval, and candidate ranking system | Active |

---

## Technology Stack

### AI / ML
* LangChain
* ChromaDB
* Ollama (`nomic-embed-text`, `phi3:mini`)

### Backend
* FastAPI
* Python 3.11+
* Pydantic

### Infrastructure
* `uv` for workspace/dependency management
* Local virtual environments

---

## Development Environment Setup

We enforce a strict, unified virtual environment graph via [`uv`](https://github.com/astral-sh/uv) to manage the entire monorepo. **Do NOT use `pip` or standard `python -m venv`.**

### Prerequisites
1. Install `uv`: [Installation Instructions](https://github.com/astral-sh/uv#installation)
2. Python 3.11+ installed
3. Install Ollama: [ollama.com](https://ollama.com)

### 1. Bootstrap Workspace
To sync the lockfile and construct the internal package links, run:
```powershell
uv sync
```
*This deterministically creates `.venv/` and wires all internal `apps/` and `packages/` into the environment.*

### 2. Prepare Local Models
Ensure Ollama is running, then execute:
```powershell
ollama pull nomic-embed-text
ollama pull phi3:mini
```

### 3. Monorepo Governance Scan
Before committing, ensure your code maintains the correct dependency boundaries:
```powershell
uv run python scripts/enforce_boundaries.py
```

---

## Workshop Task 01: Resume Analyzer

For detailed instructions on running Task 01, the API documentation, bulk ingestion, and dataset loading, see the [Task 01 README](apps/resume-analyzer/README.md).

### Quick Start
```powershell
# Boot the backend
uv run uvicorn apps.resume_analyzer.backend.api.main:app --port 8081 --reload

# Ingest the test dataset
uv run python apps/resume-analyzer/scripts/load_dataset.py --path apps/resume-analyzer/data/resumes --api-url http://localhost:8081
```

---

## Engineering Principles

This repository prioritizes:
* Architectural clarity and explicit boundaries
* Maintainability and reusability
* Deterministic pipelines
* Local-first AI workflows (offline capability)
* Production-oriented backend engineering

---

## License
MIT License
