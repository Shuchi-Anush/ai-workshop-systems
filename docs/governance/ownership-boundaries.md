# Ownership & Boundaries

## 1. Application Ownership
Each `apps/<app-name>` directory is an independent deployment unit. It owns its own:
- `pyproject.toml` (Dependencies)
- `Dockerfile` (Build execution)
- `tests/` (Integration tests)
- `prompts/` (App-specific LLM instructions)

## 2. Package Ownership
Each `packages/<package-name>` directory is an internal library. It owns its own:
- Strict semver interface definitions
- Comprehensive unit tests (100% coverage baseline target)

## 3. Infrastructure Ownership
The `infra/` directory is owned by Platform Engineering. Apps consume infrastructure configurations (e.g., pulling a Redis compose block for local testing), but apps do not define the global infrastructure.
