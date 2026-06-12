# Monorepo Governance Rules

## 1. The Two-Consumer Rule
Code must remain inside an `apps/` directory until it is actively required by a second application. Premature extraction to `packages/` creates "dead" abstractions. 

## 2. Strict One-Way Dependencies
`apps/` -> `packages/`.
Packages MUST NEVER import from `apps/`. Doing so creates circular dependencies and couples generic platforms to specific business domains.

## 3. No Cross-App Imports
`apps/resume-analyzer/` MUST NEVER import from `apps/semantic-search/`. If code is shared, it must be promoted to a package.

## 4. No God Packages
Packages named `core`, `utils`, `common`, or `shared` are explicitly banned going forward. Packages must represent a specific technical domain (e.g., `ai-vector`, `ai-observability`).
