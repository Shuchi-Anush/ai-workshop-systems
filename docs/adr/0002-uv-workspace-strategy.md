# ADR 0002: UV Workspace Strategy

**Context**: Python dependency management historically relies on Poetry or Pipenv, both of which are slow for massive monorepos.
**Decision**: We will use `uv` by Astral for workspace management.
**Tradeoffs**: `uv` is relatively new, but its Rust-based execution speed is necessary for maintaining developer velocity in a monorepo.
