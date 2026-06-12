# Infrastructure Execution Plan

## Docker Strategy
- **Base Images**: `infra/docker/base-images/python-3.11-slim.Dockerfile`. Apps build `FROM base-image`.
- **App Dockerfiles**: `apps/resume-analyzer/Dockerfile`. Builds only the app and its required workspace packages using `uv pip install`.

## Compose Layering Strategy
- `infra/services/qdrant.yml`, `infra/services/redis.yml`.
- `infra/compose/local/docker-compose.yml` will `include` the service files and the app targets, enabling local dev without polluting the app folders.

## What Stays Root-Level
- ONLY workspace configuration, CI/CD, and developer task runners (e.g., `Makefile` or `Taskfile`).
