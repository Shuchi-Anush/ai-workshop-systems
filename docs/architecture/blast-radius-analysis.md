# Blast Radius Analysis

### Phase 2: Workspace Setup
- **Radius**: Negligible. Adding `pyproject.toml` definitions doesn't break running code until we migrate requirements.

### Phase 3: Package Extraction (DANGER)
- **Radius**: Critical. Moving files breaks all imports. Tests will fail until the import rewrite strategy completes.

### Phase 4: App Migration
- **Radius**: High. Moving `task_01` to `apps/` changes import roots for the application itself.

### Phase 5: Infra Decomposition
- **Radius**: Medium. Breaks any developer's muscle-memory for running `docker compose up`. Requires new runbooks.
