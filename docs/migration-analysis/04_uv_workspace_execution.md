# UV Workspace Execution Plan

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
