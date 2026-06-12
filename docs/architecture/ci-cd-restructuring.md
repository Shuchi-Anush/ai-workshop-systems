# CI/CD Restructuring

## Current Flaw
Tests run globally across the whole repository in a single job.

## Target Architecture
1. **Matrix Testing**: GitHub actions dynamically discover modified `packages/` and `apps/`.
2. **Isolated Test Jobs**: If `ai-contracts` is modified, the CI runs tests for `ai-contracts` AND any dependent apps (`resume-analyzer`). If only `resume-analyzer` is modified, package tests are skipped to save compute.
3. **Caching**: Leverage `actions/setup-python` with `uv` caching to reduce CI times by 80%.
