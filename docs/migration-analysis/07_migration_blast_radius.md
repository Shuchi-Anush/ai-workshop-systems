# Migration Blast-Radius Simulation

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
