# Import Rewrite Strategy

During Phase 3, physical imports will be heavily modified.

**Strategy**:
1. Global regex replacement for base modules.
   - `from shared.schemas.common import` -> `from ai_contracts.schemas.common import`
   - `from shared.mocks.mock_vectordb import` -> `from ai_testing.mocks.mock_vectordb import`
2. Run `uv run ruff check --fix` and `uv run ruff format` to normalize.
3. Run `pytest tests/` repeatedly until all `ModuleNotFoundError` exceptions are resolved.
