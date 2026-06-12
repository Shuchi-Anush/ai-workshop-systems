# AI Systems Platform Monorepo - Pre-Migration Blueprint

## 1. Goal Description

This document serves as the **Safe Execution Blueprint** for the transition to the `uv` Workspace multi-app platform. We have performed a full static migration analysis of the codebase to identify dangerous couplings, unstable import hotspots, and deployment isolation violations *before* any physical files are moved.

## 2. Deep Repository Analysis & Risk Identification

Based on our static analysis, we have identified several critical breaking points that must be addressed carefully during the migration.

### A. Unstable Import Hotspots (Danger)
The file `shared/schemas/domain.py` contains `ResumeDocument` and `Candidate`. If `shared/schemas` is blindly moved into `packages/ai-contracts`, the supposedly generic contracts package will be polluted with resume-specific semantics. 
**Resolution**: `ResumeDocument` and `Candidate` must be extracted locally to `apps/resume-analyzer/schemas/` *before* the generic models (`DocumentChunk`, `BaseMetadata`) are packaged.

### B. Over-Generalized Pipelines
`shared/pipelines/` orchestrates resume ingestion and retrieval. This is highly business-specific logic. 
**Resolution**: Classified as `APP_LOCAL_ONLY`. It must be moved directly to `apps/resume-analyzer/pipelines/`.

### C. Workspace Lockfile Conflicts
If apps drift in their underlying PyTorch or SentenceTransformer versions, the entire AI platform can break.
**Resolution**: The root `pyproject.toml` will establish a strict `[tool.uv.workspace]` definition to force a unified `uv.lock` resolution across all apps and packages.

## 3. Package Extraction Readiness Matrix

| Current Module | Target Destination | Classification |
| --- | --- | --- |
| `shared/schemas/common.py` | `packages/ai-contracts` | **READY_FOR_EXTRACTION** |
| `shared/schemas/vector.py` | `packages/ai-vector` | **READY_FOR_EXTRACTION** |
| `shared/schemas/domain.py` | *Split: App + Package* | **NEEDS_REFACTOR** |
| `shared/interfaces/*` | `packages/ai-contracts` | **READY_FOR_EXTRACTION** |
| `shared/mocks/*` | `packages/ai-testing` | **READY_FOR_EXTRACTION** |
| `shared/pipelines/*` | `apps/resume-analyzer` | **APP_LOCAL_ONLY** |

## 4. Final Migration Execution Checklist

The following 10 pre-migration documents have been successfully generated under `docs/migration-analysis/`:
1. `01_import_graph_analysis.md`
2. `02_package_extraction_readiness.md`
3. `03_app_boundary_analysis.md`
4. `04_uv_workspace_execution.md`
5. `05_infrastructure_execution.md`
6. `06_ci_cd_impact_analysis.md`
7. `07_migration_blast_radius.md`
8. `08_future_scaling_simulation.md`
9. `09_repository_governance_enforcement.md`
10. `10_final_migration_checklist.md`

All architectural prerequisites have been satisfied. 

## 5. User Review Required
> [!IMPORTANT]
> The Full Static Migration Analysis is complete and the blueprint is finalized. We are now ready to cross the boundary into physical execution.
> 
> Once approved, I will begin the **Workspace Setup and Package Extraction** phase. This will involve rewriting imports, extracting `ai-contracts`, `ai-vector`, and `ai-testing`, and restructuring the `apps/` directory. Proceed?
