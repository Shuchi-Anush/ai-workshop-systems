# Phase E — Application Boundary Migration Plan (Corrected)

Per the architectural corrections, the migration has been structurally revised to establish proper namespace isolation and future scaling boundaries.

## 1. Final App Topology

To prioritize namespace hygiene over minimal folder depth, we utilize the standard Python namespace package layout (`src/` layout) while maintaining the user-requested conceptual boundary.

```text
apps/
└── resume-analyzer/
    ├── pyproject.toml
    ├── README.md
    ├── src/
    │   └── apps/
    │       └── resume_analyzer/
    │           └── backend/
    │               ├── api/
    │               ├── di/
    │               ├── parser/
    │               ├── pipelines/
    │               ├── rag/
    │               ├── ranking/
    │               ├── schemas/
    │               ├── services/
    │               └── utils/
    ├── frontend/            (Placeholder for future UI)
    └── tests/
        ├── integration/
        └── fixtures/
```

## 2. Namespace Strategy
The application namespace is strictly `apps.resume_analyzer.backend.*`. This prevents global namespace pollution and allows multiple applications (e.g., `apps.invoice_analyzer.backend.*`) to coexist cleanly within the monorepo workspace.

## 3. Import Rewrite Strategy
All imports previously pointing to `task_01_resume_rag.src.*`, `shared.pipelines.*`, or `shared.providers.*` will be surgically rewritten to:
`from apps.resume_analyzer.backend... import ...`

## 4. Backend/Frontend Boundary Rationale
Hard-separating `backend/` from `frontend/` within the app boundary prevents monolithic entanglement. When a React/Next.js frontend is introduced, it will live in `apps/resume-analyzer/frontend/` and communicate with `backend/` via API, but they will deploy and version together within the logical `resume-analyzer` app boundary.

## 5. Future Multi-App Scaling Rationale
By establishing `apps.*` as the namespace root, we lock in a scalable architecture. Future apps like `security-analyzer` or `agent-orchestrator` can be safely isolated as peer workspace packages (`apps/security-analyzer`, `apps/agent-orchestrator`), complete with their own dependencies and test suites, without risking code collision or deployment entanglement.

## 6. Test Topology Rationale
The integration tests and fixtures are physically moved to `apps/resume-analyzer/tests/`. However, to preserve "temporary root compatibility" and "current CI continuity", we will leave thin wrapper shims in the root `tests/integration/` folder. This allows `uv run pytest tests/` to execute successfully during this transitional phase, but establishes the target state where tests are inherently coupled to the applications they validate.
