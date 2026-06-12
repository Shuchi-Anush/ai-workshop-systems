# Package Extraction Matrix

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
