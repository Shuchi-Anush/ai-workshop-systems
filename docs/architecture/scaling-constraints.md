# Scaling Constraints

## GPU Workloads
Future applications will require GPU access. The separation of `workers/` inside apps allows us to deploy API pods (CPU-only, highly replicated) completely independent of Worker pods (GPU-bound, autoscaled on queue depth).

## State Management
Vector databases (Qdrant) and Relational stores (PostgreSQL) are stateful. The `infra/services/` decomposition ensures that stateful services can be managed via managed cloud services (e.g., AWS RDS) in production, while running in Docker locally, without requiring code changes.
