# Future Scaling Simulation

## Multi-Agent Orchestration App
- Can live in `apps/agent-orchestrator/`.
- Can reuse `packages/ai-observability/` for tracing agent reasoning.
- Can declare its own dependencies (`langgraph`, `openai`) without forcing the `resume-analyzer` to install them.

## GPU-Heavy Inference Workers
- `apps/resume-analyzer/workers/` can have a separate `Dockerfile.gpu` pulling from `infra/docker/base-images/cuda-12.Dockerfile`.
- Allows CPU API pods and GPU Worker pods to scale independently in Kubernetes.
