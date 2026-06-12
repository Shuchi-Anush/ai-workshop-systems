# App Boundary Analysis: `task_01_resume_rag`

## Belongs Permanently Inside the App
- `pipelines/`: Orchestration flow for resume processing.
- `prompts/`: Specific LLM instructions for resume intelligence.
- `schemas/`: `ResumeDocument`, `Candidate`, `ExperienceEntry`.
- `api/`: FastAPI routes serving the resume features.

## What Should NEVER Become Reusable Packages
- Resume chunking heuristics (e.g., splitting by "EXPERIENCE" headers).
- The specific ranking weights (e.g., scoring PyTorch higher for ML candidates).

## What Violates Future App Isolation Currently
- Depending on the root `requirements-lock.txt`.
- Running via a root `docker-compose.yml` which assumes this is the ONLY app.
