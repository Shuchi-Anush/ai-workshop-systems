# Goal Description

Perform a FULL-SCALE ZERO-TRUST RECONSTRUCTION of the `ai-workshop-systems` monorepo. This involves purging architectural cycles, fixing dependency boundary leaks, ensuring package isolation, upgrading the API for container-safe uploads, and building immutable production Docker deployments.

## User Review Required

> [!CAUTION]
> This plan heavily refactors the monorepo's internal boundaries. Please review the proposed movements of domain objects and schema definitions. In particular, the ingestion API will change from accepting a `file_path` JSON field to accepting a `multipart/form-data` file upload, which breaks existing frontend/API contracts.

## Open Questions

> [!WARNING]
> Do we want to keep `docker-compose.yml` mapped strictly to `Dockerfile.dev`, and orchestrate `Dockerfile.prod` manually, or provide a `docker-compose.prod.yml`? (I will provide a standalone `Dockerfile.prod` per instructions).

## Proposed Changes

### 1. Contract Layer Purification & Testing Decoupling (Phases 3 & 4)
We will purify `ai-contracts` so it contains all interfaces but no implementations, and decouple `ai-testing` from the `resume-analyzer` application.

#### [MODIFY] `packages/ai-contracts/src/ai_contracts/schemas/vector.py`
- Absorb the base `VectorRecord`, `EmbeddingVector`, and `VectorSearchResult` schemas directly into `ai-contracts` instead of importing them from `ai-vector`.

#### [MODIFY] `packages/ai-vector/src/ai_vector/schemas/vector.py`
- Remove definitions and simply import them from `ai-contracts`, ensuring `ai-vector` is an implementation dependent on `ai-contracts` (DAG compliance).

#### [MODIFY] `packages/ai-contracts/src/ai_contracts/pipelines/retrieval_pipeline.py`
- Remove the `ai_observability` import (`PipelineObservabilityMixin`). Dependency injection or wrapping should handle observability.

#### [DELETE] `packages/ai-testing/src/ai_testing/mocks/mock_metadata_store.py`
- This file imports `apps.resume_analyzer.backend.schemas.domain.Candidate`. It will be moved entirely into the application.

#### [NEW] `apps/resume-analyzer/tests/mocks/mock_metadata_store.py`
- Recreate the app-specific mock store here.

### 2. Package Isolation Hardening (Phase 2)
We will strictly declare all dependencies in their respective `pyproject.toml` files so wheels build and run isolated.

#### [MODIFY] `packages/ai-contracts/pyproject.toml`
- Currently correct if we remove `ai-vector` and `ai-observability` imports.

#### [MODIFY] `packages/ai-vector/pyproject.toml`
- Add `numpy>=1.24.0`
- Add `ai-contracts` dependency

#### [MODIFY] `packages/ai-testing/pyproject.toml`
- Add `numpy>=1.24.0`
- Add `ai-contracts`, `ai-vector` dependencies

#### [MODIFY] `apps/resume-analyzer/pyproject.toml`
- Add `uvicorn>=0.23.0`
- Add `python-multipart>=0.0.6`

### 3. FastAPI Modernization (Phase 5)
Remove local-machine assumptions (`file_path: str`) from the ingestion API.

#### [MODIFY] `apps/resume-analyzer/src/apps/resume_analyzer/backend/schemas/ingestion.py`
- Remove `file_path` from `IngestionRequest`.

#### [MODIFY] `apps/resume-analyzer/src/apps/resume_analyzer/backend/api/routes.py`
- Change `/ingest` route to use `fastapi.UploadFile` alongside the candidate ID and trace ID.

### 4. Docker Productionization (Phase 6)
Enforce immutable deployments without editable installs or volume overrides.

#### [MODIFY] `Dockerfile` -> `Dockerfile.dev`
- Rename the current `Dockerfile` to `Dockerfile.dev` to make explicit its reliance on editable installs.
- Update `docker-compose.yml` to point to `Dockerfile.dev`.

#### [NEW] `Dockerfile.prod`
- Create a multi-stage production build.
- **Stage 1 (Builder):** Uses `uv build` to compile wheel files (`.whl`) for all packages and apps.
- **Stage 2 (Runtime):** Copies only the wheels and `uv pip install *.whl` them into a clean container, dropping all dev tooling and editable links.

## Verification Plan

### Automated Tests
- `uv run pytest apps/resume-analyzer/tests/` to verify tests pass with the newly moved mocks.

### Manual Verification
- **Isolated Wheel Build:** `uv build` inside `packages/ai-contracts` and `packages/ai-vector`.
- **Production Container Boot:** `docker build -f Dockerfile.prod -t ai_workshop_prod .` followed by `docker run --rm -p 8000:8000 ai_workshop_prod` to ensure it boots without volume mounts.
