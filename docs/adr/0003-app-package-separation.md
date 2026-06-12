# ADR 0003: App vs Package Separation

**Context**: Shared code often degrades into a highly-coupled monolith.
**Decision**: Adopt the Two-Consumer Rule. Code lives in `apps/` until two applications explicitly need it. Then it is abstracted into a specific `packages/<domain>`.
**Tradeoffs**: This causes slight duplication initially, but prevents catastrophic premature abstractions.
