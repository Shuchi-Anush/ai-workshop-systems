# Package Extraction Readiness Report

| Module | Classification | Justification |
| --- | --- | --- |
| `shared/schemas/common.py` | **READY_FOR_EXTRACTION** | Purely generic Pydantic bases. |
| `shared/schemas/vector.py` | **READY_FOR_EXTRACTION** | Generic vector math/search schemas. |
| `shared/schemas/domain.py` | **NEEDS_REFACTOR** | Contains `ResumeDocument` and `Candidate`. These are resume-specific and must be extracted to the app layer before the rest of the file becomes `ai-contracts`. |
| `shared/interfaces/*` | **READY_FOR_EXTRACTION** | Pure abstract base classes for AI primitives. |
| `shared/mocks/*` | **READY_FOR_EXTRACTION** | Generic testing mocks. Belongs in `ai-testing`. |
| `shared/providers/*` | **READY_FOR_EXTRACTION** | Dependency injection registry. Can be part of `ai-core`. |
| `shared/pipelines/*` | **APP_LOCAL_ONLY** | Orchestration of resume ingestion and retrieval. Do not extract to packages. Move to `apps/resume-analyzer/pipelines/`. |
