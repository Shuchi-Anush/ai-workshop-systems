# Monorepo Architectural Dependency Rules

To maintain production stability and microservice scalability, the `ai-workshop-systems` monorepo strictly enforces a Directed Acyclic Graph (DAG) for dependency management.

## 1. Global Hierarchy

The fundamental dependency direction must strictly flow downwards:
`apps` -> `packages/services` -> `contracts`

## 2. Strict Rules

- **Rule 1: Apps Cannot Be Imported**
  - Code inside `packages/*` MUST NEVER import code from `apps/*`.
  - Mocks that use application-specific domain models must live in the app's `tests/mocks/` directory, never in `packages/ai-testing`.

- **Rule 2: Contracts Cannot Import Implementations**
  - Code inside `ai-contracts` MUST NEVER import concrete implementations (like `ai-vector` or `ai-observability`).
  - Interfaces are strictly defined in `ai-contracts` and downstream packages implement them.
  - Cyclic dependencies between contracts and implementations will instantly fail CI build processes.

- **Rule 3: Strict Dependency Declarations**
  - Workspace flattening cannot be trusted. If a package imports `numpy`, `fastapi`, or `ai-contracts`, it MUST be explicitly listed in that package's `pyproject.toml`.
  - Transitive borrowing is illegal.

## 3. Deployment Rules

- **Rule 4: Immutability**
  - Production deployments use `Dockerfile.prod` leveraging multi-stage isolated wheel builds.
  - Editable installs (`uv sync` or `pip install -e`) and bind mounts (`- ./apps:/app/apps`) are strictly prohibited in production containers.
  - The API cannot assume access to local disk structures; all payloads must use `multipart/form-data` (e.g. `fastapi.UploadFile`) or distributed storage URIs.
