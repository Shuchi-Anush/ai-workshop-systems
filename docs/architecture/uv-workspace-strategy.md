# UV Workspace Strategy

## Mechanism
The root `pyproject.toml` will define a `[tool.uv.workspace]` block including `members = ["apps/*", "packages/*"]`.

## Benefits
1. **Single Lockfile**: Ensures that if `ai-vector` requires `numpy==1.24`, `resume-analyzer` doesn't accidentally install `numpy==1.26` and cause runtime faults.
2. **Fast Virtual Environments**: UV provisions environments across the entire monorepo in milliseconds.
3. **Local Linking**: Apps can `import ai_vector` directly without requiring `pip install -e` scripts.
