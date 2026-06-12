# ADR 0005: Dependency Governance

**Context**: Apps need to pull internal packages easily without publishing to PyPI.
**Decision**: Internal dependencies will be linked via `workspace = true` in `pyproject.toml`.
**Tradeoffs**: This strictly ties packages to the monorepo lifecycle.
