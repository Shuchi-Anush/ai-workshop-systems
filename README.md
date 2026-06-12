# AI Workshop Systems

Production-oriented AI systems monorepo for building, testing, and orchestrating scalable AI engineering workflows.

The repository is structured around modular AI tasks, shared infrastructure, reusable orchestration utilities, and production-minded backend architectures.

---

## Core Objectives

This workspace exists to support:

* Retrieval-Augmented Generation (RAG) systems
* FastAPI-based AI services
* Local LLM orchestration
* Vector search pipelines
* Resume intelligence systems
* Embedding and ranking workflows
* AI engineering experimentation
* Production-style architecture design

The focus is not rapid prototyping alone, but engineering maintainable, extensible, and operationally structured AI systems.

---

## Repository Philosophy

The monorepo enforces:

* Modular task isolation
* Shared infrastructure reuse
* Explicit pipeline boundaries
* Production-oriented backend structure
* Reproducible local development
* AI-assisted engineering workflows

Each task behaves as an independently evolvable AI subsystem while sharing common tooling, utilities, and orchestration layers.

---

## Current Tasks

| Task                 | Description                                                        | Status             |
| -------------------- | ------------------------------------------------------------------ | ------------------ |
| `task_01_resume_rag` | Resume parsing, embedding, retrieval, and candidate ranking system | Active Development |

---

## Repository Structure

```text
ai-workshop-systems/
│
├── docs/                       # Architecture docs, workflows, ADRs
│   └── workflows/
│
├── notes/                      # Research notes and engineering references
│
├── scripts/                    # Automation and setup scripts
│
├── shared/                     # Shared reusable infrastructure
│   ├── llm/
│   ├── parsers/
│   ├── schemas/
│   └── utils/
│
├── task_01_resume_rag/         # Resume RAG pipeline
│   ├── data/
│   ├── notebooks/
│   ├── outputs/
│   ├── src/
│   ├── tests/
│   ├── README.md
│   └── requirements.txt
│
├── .env.example
├── .gitignore
├── README.md
└── requirements-lock.txt
```

---

## Shared Infrastructure

The `shared/` layer contains reusable modules intended to prevent duplicated implementations across tasks.

Examples include:

* LLM wrappers
* Document parsers
* Shared schemas
* Logging utilities
* Common validation contracts
* Reusable orchestration helpers

---

## Technology Stack

### AI / ML

* LangChain
* Sentence Transformers
* FAISS
* HuggingFace Transformers
* Ollama

### Backend

* FastAPI
* Python
* Pydantic

### Infrastructure

* Docker
* GitHub
* VS Code
* Local virtual environments

---

## Development Environment

### Create Environment

```bash
python -m venv venv
```

### Activate

**Windows**

```powershell
venv\Scripts\Activate.ps1
```

### Install Dependencies

```bash
pip install -r task_01_resume_rag/requirements.txt
```

---

## Git Workflow

```bash
git pull
git add .
git commit -m "Meaningful commit message"
git push
```

---

## Engineering Principles

This repository prioritizes:

* Architectural clarity
* Explicit boundaries
* Maintainability
* Reusability
* Deterministic pipelines
* Local-first AI workflows
* Production-oriented backend engineering

---

## Future Roadmap

Planned future systems include:

* Multi-agent orchestration
* LLM routing systems
* Evaluation pipelines
* AI observability tooling
* Knowledge graph integration
* Distributed retrieval systems
* Multi-modal ingestion pipelines
* Secure AI infrastructure

---

## License

MIT License
