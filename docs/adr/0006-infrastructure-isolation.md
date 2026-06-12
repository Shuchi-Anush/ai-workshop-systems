# ADR 0006: Infrastructure Isolation

**Context**: Infrastructure logic mixed with application logic prevents independent scaling.
**Decision**: All operational configs (Docker, Compose, K8s) live in `infra/`. Applications only define the execution entrypoint (`Dockerfile`).
**Tradeoffs**: Increases repository directory depth, but clarifies ownership for DevOps/Platform engineers.
