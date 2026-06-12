# Dependency Governance

## 1. Unified Workspace
The monorepo uses `uv workspaces`. All packages and apps belong to a single workspace defined in the root `pyproject.toml` to ensure dependency resolution and prevent version conflicts across the platform.

## 2. Isolation
Despite the unified workspace, an application's `pyproject.toml` MUST explicitly declare the internal packages it depends on (e.g., `ai-vector = { workspace = true }`).

## 3. Leakage Prevention
Infrastructure dependencies (e.g., `kubernetes` python client) MUST NOT be present in application dependency lists. Operational concerns are isolated.
