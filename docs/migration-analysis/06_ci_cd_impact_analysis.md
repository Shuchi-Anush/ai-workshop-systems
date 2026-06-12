# CI/CD Impact Analysis

## Matrix Testing Strategy
- The GitHub action will use a script to detect changed paths.
- If `packages/ai-vector/` changes, the CI dynamically generates a test matrix containing `['packages/ai-vector', 'apps/resume-analyzer']` because the app depends on the package.

## Ruff/Mypy Isolation
- `uv run ruff check` and `uv run mypy` will be executed at the workspace root, applying to all packages and apps uniformly to ensure monorepo-wide code quality.

## Caching Strategy
- Use `actions/setup-python` with `cache: 'uv'`.
- This ensures that heavy ML dependency downloads (e.g., Torch, HuggingFace Hub) are cached aggressively across CI runs.
