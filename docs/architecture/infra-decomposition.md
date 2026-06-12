# Infrastructure Decomposition

## Goal
Eliminate root-level `docker-compose.yml` and `Dockerfile`.

## Target Structure
- `infra/services/`: Discrete compose files for individual services (e.g., `redis.yml`, `postgres.yml`, `qdrant.yml`).
- `infra/compose/local/`: Aggregates services for local development. `docker compose -f infra/compose/local/docker-compose.yml up`.
- `infra/compose/prod/`: Production-ready configurations.
- `infra/docker/base-images/`: Shared multi-stage Python/GPU base images. Apps reference these bases rather than repeating `apt-get install` commands.
