import os
from pathlib import Path

base_dir = Path("d:/ai-workshop-systems/docs/migration-analysis")
base_dir.mkdir(parents=True, exist_ok=True)

files_content = {
    "01_import_graph_analysis.md": """# Complete Import Graph Analysis

## Current Import Graph
The current repository heavily relies on absolute imports rooted at the monorepo root:
- `shared.schemas.*`
- `shared.interfaces.*`
- `shared.mocks.*`
- `shared.pipelines.*`

## Dependency Direction Graph
- **Current**: `task_01_resume_rag` -> `shared`
- **Target**: `apps/resume-analyzer` -> `packages/ai-*`

## Circular Dependency Detection
- Currently, no circular dependencies exist between `shared/` and `task_01_resume_rag/`. 
- **Danger**: `shared/pipelines/` imports from `shared/interfaces/` and `shared/schemas/`. If pipelines are moved to `apps/resume-analyzer/pipelines/`, they must NOT be imported back into any `packages/`.

## Unstable Import Hotspots
- `shared/schemas/domain.py`: Currently contains `ResumeDocument` and `Candidate`. If `shared/schemas` is blindly moved to `packages/ai-contracts`, the contract package becomes polluted with resume semantics.
- **Resolution**: `ResumeDocument` and `Candidate` must be decoupled into `apps/resume-analyzer/schemas/`.
""",

    "02_package_extraction_readiness.md": """# Package Extraction Readiness Report

| Module | Classification | Justification |
| --- | --- | --- |
| `shared/schemas/common.py` | **READY_FOR_EXTRACTION** | Purely generic Pydantic bases. |
| `shared/schemas/vector.py` | **READY_FOR_EXTRACTION** | Generic vector math/search schemas. |
| `shared/schemas/domain.py` | **NEEDS_REFACTOR** | Contains `ResumeDocument` and `Candidate`. These are resume-specific and must be extracted to the app layer before the rest of the file becomes `ai-contracts`. |
| `shared/interfaces/*` | **READY_FOR_EXTRACTION** | Pure abstract base classes for AI primitives. |
| `shared/mocks/*` | **READY_FOR_EXTRACTION** | Generic testing mocks. Belongs in `ai-testing`. |
| `shared/providers/*` | **READY_FOR_EXTRACTION** | Dependency injection registry. Can be part of `ai-core`. |
| `shared/pipelines/*` | **APP_LOCAL_ONLY** | Orchestration of resume ingestion and retrieval. Do not extract to packages. Move to `apps/resume-analyzer/pipelines/`. |
""",

    "03_app_boundary_analysis.md": """# App Boundary Analysis: `task_01_resume_rag`

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
""",

    "04_uv_workspace_execution.md": """# UV Workspace Execution Plan

## Root Workspace Strategy
- `pyproject.toml` at the root will define `[tool.uv.workspace]`.
- Members: `["apps/*", "packages/*"]`.
- The root will manage a unified `uv.lock` file to guarantee version determinism across the entire monorepo.

## Package-Local Strategy
- Each package (e.g., `packages/ai-vector/pyproject.toml`) will declare minimal generic dependencies (e.g., `numpy`, `pydantic`).

## App-Local Strategy
- Each app (e.g., `apps/resume-analyzer/pyproject.toml`) will declare heavy ML dependencies (e.g., `sentence-transformers`, `faiss-cpu`) AND internal packages via `ai-vector = { workspace = true }`.

## Conflict Governance
- By utilizing a single workspace lockfile, if `app-a` requires `torch==2.0` and `app-b` requires `torch==2.2`, `uv` will raise a resolution error at the root, forcing Platform Engineers to align the monorepo versions. This prevents silent runtime failures across deployed apps.
""",

    "05_infrastructure_execution.md": """# Infrastructure Execution Plan

## Docker Strategy
- **Base Images**: `infra/docker/base-images/python-3.11-slim.Dockerfile`. Apps build `FROM base-image`.
- **App Dockerfiles**: `apps/resume-analyzer/Dockerfile`. Builds only the app and its required workspace packages using `uv pip install`.

## Compose Layering Strategy
- `infra/services/qdrant.yml`, `infra/services/redis.yml`.
- `infra/compose/local/docker-compose.yml` will `include` the service files and the app targets, enabling local dev without polluting the app folders.

## What Stays Root-Level
- ONLY workspace configuration, CI/CD, and developer task runners (e.g., `Makefile` or `Taskfile`).
""",

    "06_ci_cd_impact_analysis.md": """# CI/CD Impact Analysis

## Matrix Testing Strategy
- The GitHub action will use a script to detect changed paths.
- If `packages/ai-vector/` changes, the CI dynamically generates a test matrix containing `['packages/ai-vector', 'apps/resume-analyzer']` because the app depends on the package.

## Ruff/Mypy Isolation
- `uv run ruff check` and `uv run mypy` will be executed at the workspace root, applying to all packages and apps uniformly to ensure monorepo-wide code quality.

## Caching Strategy
- Use `actions/setup-python` with `cache: 'uv'`.
- This ensures that heavy ML dependency downloads (e.g., Torch, HuggingFace Hub) are cached aggressively across CI runs.
""",

    "07_migration_blast_radius.md": """# Migration Blast-Radius Simulation

## 1. Import Re-writing (High Risk)
- **Risk**: Moving `shared/schemas` to `packages/ai-contracts/schemas` breaks all app imports.
- **Rollback**: Git revert.
- **Validation**: `uv run pytest tests/` must pass before commit.

## 2. Docker Restructuring (Medium Risk)
- **Risk**: Deleting root `Dockerfile` breaks automated deployment scripts or developer muscle memory.
- **Validation**: `docker build -f apps/resume-analyzer/Dockerfile .` must successfully build the container.

## 3. UV Workspace Activation (Low Risk)
- **Risk**: Minor locking conflicts.
- **Validation**: `uv lock` must succeed without downgrading critical application dependencies.
""",

    "08_future_scaling_simulation.md": """# Future Scaling Simulation

## Multi-Agent Orchestration App
- Can live in `apps/agent-orchestrator/`.
- Can reuse `packages/ai-observability/` for tracing agent reasoning.
- Can declare its own dependencies (`langgraph`, `openai`) without forcing the `resume-analyzer` to install them.

## GPU-Heavy Inference Workers
- `apps/resume-analyzer/workers/` can have a separate `Dockerfile.gpu` pulling from `infra/docker/base-images/cuda-12.Dockerfile`.
- Allows CPU API pods and GPU Worker pods to scale independently in Kubernetes.
""",

    "09_repository_governance_enforcement.md": """# Repository Governance Enforcement

## CODEOWNERS
```text
/infra/                   @platform-engineering
/packages/                @platform-engineering
/apps/resume-analyzer/    @resume-team
/docs/adr/                @architecture-board
```

## Package Extraction Approval Workflow
1. Developer identifies code used by 2+ apps.
2. Developer submits PR to move code to `packages/`.
3. PR requires `@architecture-board` approval to ensure the abstraction isn't leaking domain semantics.
""",

    "10_final_migration_checklist.md": """# Final Pre-Migration Execution Checklist

Before moving any folders or rewriting imports, confirm:

- [ ] `docs/migration-analysis/` has been generated and reviewed.
- [ ] Domain logic (`ResumeDocument`, `Candidate`) has been identified for extraction out of `shared/schemas/domain.py`.
- [ ] `shared/pipelines/` has been identified as APP_LOCAL_ONLY.
- [ ] `pyproject.toml` workspace root configuration is designed.
- [ ] Docker base image strategy is documented.
- [ ] Developers are notified of an impending repository freeze during the physical move.

**STATUS**: Ready for physical execution upon architect approval.
"""
}

for path_str, content in files_content.items():
    full_path = base_dir / path_str
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

print(f"Successfully generated {len(files_content)} migration analysis documents.")
