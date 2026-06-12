# Developer Workflow Standardization

This implementation plan focuses entirely on developer-experience (DevEx) standardization, execution consistency, and environment robustness.

## 1. Executive Assessment
The architecture and package topology are stable and structurally sound. However, the runtime shell experience, VSCode integration, and legacy documentation are aggressively guiding developers to break out of the `uv` workspace constraint. By following legacy `README.md` instructions or utilizing stale scripts, developers are inadvertently creating phantom `venv` environments using global Python distributions, thereby rendering the monorepo graph invisible to `pytest` and IDE analysis tools.

## 2. Root Cause Analysis
- **Shell Startup Bypass**: Without automatic shell hooks or explicit instructions, terminal sessions inherently default to the `PATH`'s global Python. If a developer runs `pytest`, the global interpreter executes without awareness of the `hatchling` editable install bindings.
- **Legacy Documentation Leakage**: The `README.md` actively encourages `python -m venv venv` and `pip install -r requirements.txt`. This creates a non-standard `venv` directory that `uv` does not recognize, fracturing dependency resolution.
- **Ghost Scripts**: Stale scripts like `scripts/runtime/setup.ps1` contain hardcoded legacy commands (`pip install -r requirements-lock.txt`) which bypass the `uv` lockfile entirely.

## 3. Runtime Execution Analysis
- `uv run <command>` provides **stateless execution guarantee**. It intercepts the command, guarantees the virtual environment is populated according to the `uv.lock`, activates it inline, and executes the command.
- The `.venv/` directory is the **stateful execution graph**. Activating it (`.venv\Scripts\activate`) mutates the current shell session.
- To prevent ambiguity, the developer contract must prioritize stateless `uv run` over manual `.venv` shell mutations whenever possible.

## 4. VSCode & Terminal Analysis
- We successfully stabilized VSCode Python extension resolution by pinning `"python.defaultInterpreterPath"` in `.vscode/settings.json`.
- However, VSCode Tasks and generic launch configurations are missing. Providing a standardized `.vscode/tasks.json` converts ambiguous CLI interactions into deterministic GUI buttons (Run Tests, Start API, Sync Dependencies).

## 5. Shell Bootstrap Strategy
- A dedicated `scripts/setup.ps1` should wrap `uv sync`.
- `README.md` must be entirely rewritten for the `uv` era, explicitly banning `pip install` and `python -m venv`.

## 6. Recommended Developer Contract
The canonical execution workflow for all developers onboarding to this platform:

1. **Bootstrap**: `uv sync`
2. **Execute Tests**: `uv run pytest tests/`
3. **Run API**: `uv run fastapi dev apps/resume-analyzer/src/apps/resume_analyzer/backend/main.py`
4. **Shell Rules**: Developers are forbidden from using `pip` inside the monorepo.

## 7. Exact Fixes to Apply NOW

### [DELETE] Stale Scripts
- `scripts/runtime/setup.ps1`
- `scripts/runtime/run_task1.ps1`
- `scripts/run_task1.ps1`
- `scripts/setup.ps1`

### [NEW] `scripts/setup.ps1`
A unified developer bootstrap script:
```powershell
Write-Host "Bootstrapping AI Workshop Systems..."
uv sync
Write-Host "Setup complete. Use 'uv run' to execute commands."
```

### [NEW] `scripts/dev.ps1`
A script to spin up local dev environments safely:
```powershell
Write-Host "Starting Resume Analyzer API..."
uv run uvicorn task_01_resume_rag.src.api.main:app --reload
```

### [NEW] `.vscode/tasks.json`
Standardized IDE actions for testing, syncing, and running the server using `uv run`.

### [MODIFY] `README.md`
Scrub all mentions of `pip`, `requirements.txt`, and standard `venv`. Replace with `uv sync` and `uv run`.

## 8. Recommended Automation Scripts
- Include an entrypoint script to cleanly wrap backend boot sequences. This prevents shell misconfigurations during local dev.

## 9. Phase F Runtime Cleanup Recommendations
- **Docker Drift**: `docker-compose.yml` mounts `task_01_resume_rag`. During Phase F, this must map natively to `apps/resume-analyzer`.
- **Requirements files**: Once `uv.lock` is fully adopted, `requirements.txt` and `requirements-lock.txt` should be deleted.

## 10. Final Platform Verdict
By standardizing on `uv run` and deleting all legacy `pip`-based setup logic, the repository will achieve total deterministic immutability. Every execution will behave exactly the same way on every machine.

---
> [!IMPORTANT]
> User Review Required
> Please approve this plan so I can proceed with the destructive cleanup of legacy scripts and the creation of the final dev standard files.
