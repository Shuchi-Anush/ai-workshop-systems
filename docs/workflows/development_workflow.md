# Development Workflow

* **Virtual Environment**: Use `python -m venv venv`.
* **Environment Variables**: Managed via `.env` based on `.env.example`.
* **Execution**: Run API locally via `uvicorn task_01_resume_rag.src.api.main:app --reload`.
* **Iterative Testing**: Use Jupyter notebooks in `task_01_resume_rag/notebooks/` for rapid prototyping of chunking and embedding logic before migrating to `src/`.
