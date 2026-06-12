# Repository Governance Enforcement

## CODEOWNERS
```text
/infra/                   @platform-engineering
/packages/                @platform-engineering
/apps/resume-analyzer/    @resume-team
/docs/adr/                @architecture-board
```

## Package Extraction Approval Workflow
1. Developer identifies code used by 2+ apps.
2. Developer submits PR to move code to `packages/`.
3. PR requires `@architecture-board` approval to ensure the abstraction isn't leaking domain semantics.
