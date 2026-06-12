# Complete Import Graph Analysis

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
