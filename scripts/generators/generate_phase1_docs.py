import os
from pathlib import Path

base_dir = Path("d:/ai-workshop-systems/docs")
dirs = [
    "architecture",
    "adr",
    "workflows",
    "governance"
]

for d in dirs:
    (base_dir / d).mkdir(parents=True, exist_ok=True)

files_content = {
    "governance/monorepo-rules.md": """# Monorepo Governance Rules

## 1. The Two-Consumer Rule
Code must remain inside an `apps/` directory until it is actively required by a second application. Premature extraction to `packages/` creates "dead" abstractions. 

## 2. Strict One-Way Dependencies
`apps/` -> `packages/`.
Packages MUST NEVER import from `apps/`. Doing so creates circular dependencies and couples generic platforms to specific business domains.

## 3. No Cross-App Imports
`apps/resume-analyzer/` MUST NEVER import from `apps/semantic-search/`. If code is shared, it must be promoted to a package.

## 4. No God Packages
Packages named `core`, `utils`, `common`, or `shared` are explicitly banned going forward. Packages must represent a specific technical domain (e.g., `ai-vector`, `ai-observability`).
""",

    "governance/ownership-boundaries.md": """# Ownership & Boundaries

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
""",

    "governance/dependency-rules.md": """# Dependency Governance

## 1. Unified Workspace
The monorepo uses `uv workspaces`. All packages and apps belong to a single workspace defined in the root `pyproject.toml` to ensure dependency resolution and prevent version conflicts across the platform.

## 2. Isolation
Despite the unified workspace, an application's `pyproject.toml` MUST explicitly declare the internal packages it depends on (e.g., `ai-vector = { workspace = true }`).

## 3. Leakage Prevention
Infrastructure dependencies (e.g., `kubernetes` python client) MUST NOT be present in application dependency lists. Operational concerns are isolated.
""",

    "architecture/dependency-dag.md": """# Dependency DAG

```mermaid
graph TD
    subgraph Apps
        A[resume-analyzer]
        B[future-semantic-search]
    end

    subgraph Packages
        C[ai-retrieval]
        D[ai-vector]
        E[ai-observability]
        F[ai-contracts]
        G[ai-errors]
    end

    subgraph Infra
        H[infra/docker/base-images]
        I[infra/services/qdrant]
    end

    A --> C
    A --> D
    A --> E
    B --> D
    B --> E

    C --> F
    C --> G
    D --> F
    D --> G
    E --> F

    A -.->|Deployed Via| H
    B -.->|Deployed Via| H
    A -.->|Connects To| I
```
""",

    "architecture/package-extraction-matrix.md": """# Package Extraction Matrix

Mapping current `shared/` structure to target `packages/` structure:

| Current Path | Target Package | Rationale |
| --- | --- | --- |
| `shared/schemas/common.py` | `ai-contracts` | Foundational schemas are contracts. |
| `shared/schemas/domain.py` | `ai-contracts` | Generic domain concepts. |
| `shared/schemas/vector.py` | `ai-vector` | Vector specifics belong in vector domain. |
| `shared/interfaces/parser.py` | `ai-contracts` | Base contracts. |
| `shared/interfaces/vectordb.py` | `ai-vector` | Vector DB contracts. |
| `shared/mocks/mock_vectordb.py` | `ai-testing` | Mocks belong in a testing utility package. |
| `shared/pipelines/` | `apps/resume-analyzer/pipelines/` | App-specific orchestration should NOT be extracted yet. |
""",

    "architecture/import-rewrite-strategy.md": """# Import Rewrite Strategy

During Phase 3, physical imports will be heavily modified.

**Strategy**:
1. Global regex replacement for base modules.
   - `from shared.schemas.common import` -> `from ai_contracts.schemas.common import`
   - `from shared.mocks.mock_vectordb import` -> `from ai_testing.mocks.mock_vectordb import`
2. Run `uv run ruff check --fix` and `uv run ruff format` to normalize.
3. Run `pytest tests/` repeatedly until all `ModuleNotFoundError` exceptions are resolved.
""",

    "architecture/infra-decomposition.md": """# Infrastructure Decomposition

## Goal
Eliminate root-level `docker-compose.yml` and `Dockerfile`.

## Target Structure
- `infra/services/`: Discrete compose files for individual services (e.g., `redis.yml`, `postgres.yml`, `qdrant.yml`).
- `infra/compose/local/`: Aggregates services for local development. `docker compose -f infra/compose/local/docker-compose.yml up`.
- `infra/compose/prod/`: Production-ready configurations.
- `infra/docker/base-images/`: Shared multi-stage Python/GPU base images. Apps reference these bases rather than repeating `apt-get install` commands.
""",

    "architecture/uv-workspace-strategy.md": """# UV Workspace Strategy

## Mechanism
The root `pyproject.toml` will define a `[tool.uv.workspace]` block including `members = ["apps/*", "packages/*"]`.

## Benefits
1. **Single Lockfile**: Ensures that if `ai-vector` requires `numpy==1.24`, `resume-analyzer` doesn't accidentally install `numpy==1.26` and cause runtime faults.
2. **Fast Virtual Environments**: UV provisions environments across the entire monorepo in milliseconds.
3. **Local Linking**: Apps can `import ai_vector` directly without requiring `pip install -e` scripts.
""",

    "architecture/ci-cd-restructuring.md": """# CI/CD Restructuring

## Current Flaw
Tests run globally across the whole repository in a single job.

## Target Architecture
1. **Matrix Testing**: GitHub actions dynamically discover modified `packages/` and `apps/`.
2. **Isolated Test Jobs**: If `ai-contracts` is modified, the CI runs tests for `ai-contracts` AND any dependent apps (`resume-analyzer`). If only `resume-analyzer` is modified, package tests are skipped to save compute.
3. **Caching**: Leverage `actions/setup-python` with `uv` caching to reduce CI times by 80%.
""",

    "architecture/scaling-constraints.md": """# Scaling Constraints

## GPU Workloads
Future applications will require GPU access. The separation of `workers/` inside apps allows us to deploy API pods (CPU-only, highly replicated) completely independent of Worker pods (GPU-bound, autoscaled on queue depth).

## State Management
Vector databases (Qdrant) and Relational stores (PostgreSQL) are stateful. The `infra/services/` decomposition ensures that stateful services can be managed via managed cloud services (e.g., AWS RDS) in production, while running in Docker locally, without requiring code changes.
""",

    "architecture/blast-radius-analysis.md": """# Blast Radius Analysis

### Phase 2: Workspace Setup
- **Radius**: Negligible. Adding `pyproject.toml` definitions doesn't break running code until we migrate requirements.

### Phase 3: Package Extraction (DANGER)
- **Radius**: Critical. Moving files breaks all imports. Tests will fail until the import rewrite strategy completes.

### Phase 4: App Migration
- **Radius**: High. Moving `task_01` to `apps/` changes import roots for the application itself.

### Phase 5: Infra Decomposition
- **Radius**: Medium. Breaks any developer's muscle-memory for running `docker compose up`. Requires new runbooks.
""",

    "adr/0001-monorepo-strategy.md": """# ADR 0001: Monorepo Strategy

**Context**: The organization needs to deploy multiple AI systems sharing core operational primitives (tracing, schemas, vector handling). Managing these as multi-repos leads to version drift and operational nightmare.
**Decision**: We will utilize a Python Monorepo based on `uv workspaces` separating `apps/` from `packages/`.
**Tradeoffs**: Monorepos require stricter CI/CD caching and import discipline. The benefit of synchronized versioning outweighs the initial CI complexity.
""",

    "adr/0002-uv-workspace-strategy.md": """# ADR 0002: UV Workspace Strategy

**Context**: Python dependency management historically relies on Poetry or Pipenv, both of which are slow for massive monorepos.
**Decision**: We will use `uv` by Astral for workspace management.
**Tradeoffs**: `uv` is relatively new, but its Rust-based execution speed is necessary for maintaining developer velocity in a monorepo.
""",

    "adr/0003-app-package-separation.md": """# ADR 0003: App vs Package Separation

**Context**: Shared code often degrades into a highly-coupled monolith.
**Decision**: Adopt the Two-Consumer Rule. Code lives in `apps/` until two applications explicitly need it. Then it is abstracted into a specific `packages/<domain>`.
**Tradeoffs**: This causes slight duplication initially, but prevents catastrophic premature abstractions.
""",

    "adr/0004-vector-storage-abstraction.md": """# ADR 0004: Vector Storage Abstraction

**Context**: AI Apps rapidly shift vector database vendors (FAISS -> Qdrant -> Pinecone).
**Decision**: Enforce `IVectorDB` interface at the package level (`ai-vector`). Applications must never import vendor-specific SDKs into business logic.
**Tradeoffs**: Requires maintaining wrapper classes, but guarantees future migration safety.
""",

    "adr/0005-dependency-governance.md": """# ADR 0005: Dependency Governance

**Context**: Apps need to pull internal packages easily without publishing to PyPI.
**Decision**: Internal dependencies will be linked via `workspace = true` in `pyproject.toml`.
**Tradeoffs**: This strictly ties packages to the monorepo lifecycle.
""",

    "adr/0006-infrastructure-isolation.md": """# ADR 0006: Infrastructure Isolation

**Context**: Infrastructure logic mixed with application logic prevents independent scaling.
**Decision**: All operational configs (Docker, Compose, K8s) live in `infra/`. Applications only define the execution entrypoint (`Dockerfile`).
**Tradeoffs**: Increases repository directory depth, but clarifies ownership for DevOps/Platform engineers.
"""
}

for path_str, content in files_content.items():
    full_path = base_dir / path_str
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

print(f"Successfully generated {len(files_content)} governance, architecture, and ADR documents.")
