# Final Pre-Migration Execution Checklist

Before moving any folders or rewriting imports, confirm:

- [ ] `docs/migration-analysis/` has been generated and reviewed.
- [ ] Domain logic (`ResumeDocument`, `Candidate`) has been identified for extraction out of `shared/schemas/domain.py`.
- [ ] `shared/pipelines/` has been identified as APP_LOCAL_ONLY.
- [ ] `pyproject.toml` workspace root configuration is designed.
- [ ] Docker base image strategy is documented.
- [ ] Developers are notified of an impending repository freeze during the physical move.

**STATUS**: Ready for physical execution upon architect approval.
