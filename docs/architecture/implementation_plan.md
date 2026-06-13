# Final Hardening & Workshop Optimization Plan

The goal is to finalize `Task 01` (Resume Analyzer) and perform a complete hardening pass for the `ai-workshop-systems` monorepo. This plan ensures we meet all workshop requirements (bulk ingestion, dataset scripts, API stability, and governance) while maintaining the dual-zone monorepo strategy.

## Proposed Changes

### Phase 1: Task 01 Finalization (Persistence & Stability)
- **Replace `InMemoryMetadataStore`** with `LocalJSONMetadataStore` in `factories.py`. This ensures that metadata survives a server restart (syncing to `chroma_db/metadata.json`) to match ChromaDB's persistence.
- **Edge Case Handling**: Update `/ingest` to handle duplicate `candidate_id` safely and skip gracefully or overwrite. Update parser to handle malformed/empty PDFs safely.

### Phase 2: Bulk Ingestion Support
- **New Endpoint**: `POST /bulk-ingest` in `routes.py`.
  - Accepts `List[UploadFile]`.
  - Sequentially ingests files (async-safe) to avoid overloading local Ollama embeddings.
  - Automatically derives `candidate_id` from the filename (e.g., stripping `.pdf`).
  - Stores uploaded PDFs physically in `apps/resume-analyzer/data/resumes/`.
  - Returns a detailed summary of successful and failed ingestions.

### Phase 3: Dataset Utilities
- **New CLI Script**: `apps/resume-analyzer/scripts/load_dataset.py`.
  - Recursively walks a specified directory to find `.pdf` files.
  - Uses `requests` to hit the `/bulk-ingest` API in batches.
  - Generates an ingestion summary and skips corrupt files.

### Phase 4: API & DX Improvements
- **New Endpoints** in `routes.py`:
  - `GET /stats`: Returns total candidates and chunks in the system.
  - `POST /reset-db`: Clears ChromaDB and the JSON Metadata store for easy workshop resets.
  - `GET /candidates`: Lists all ingested candidates.
  - `GET /candidate/{id}`: Returns details and chunks for a specific candidate.
- **Swagger Updates**: Add descriptions and structured response models.

### Phase 5: Monorepo Governance
- **Governance Script**: Create `scripts/enforce_boundaries.py` at the root.
  - Scans `apps/` to ensure NO imports point to other `apps/`.
  - Scans `packages/` to ensure NO imports point to `apps/`.
  - Only `apps/` -> `packages/` and `packages/` -> `packages/` are allowed.
  - This ensures architectural purity for future tasks.

### Phase 6 & 7: Testing & Documentation
- **Testing**: Run the end-to-end flow using the new `load_dataset.py` and API endpoints. Validate Ollama stability during bulk ingestion.
- **Documentation**: Update `README.md` at the root and `apps/resume-analyzer/README.md` to reflect the new endpoints, the dual-zone architecture, and exact commands for workshop attendees.

## User Review Required
> [!IMPORTANT]
> Is `LocalJSONMetadataStore` acceptable for the workshop, or would you prefer a `SQLite` store? JSON is simpler and avoids dependency issues, making it highly "workshop-safe".
> Are there any specific Kaggle dataset paths we should default to in the `load_dataset.py` script?
