# Ingestion Pipeline

The ingestion pipeline must be highly deterministic to ensure predictable chunk generation.

1. **Parsing**: PDF/DOCX -> Raw Text.
2. **Sectioning**: Rule-based or LLM-assisted identification of structural headers.
3. **Chunking**: Sections are split into `DocumentChunk`s. A chunk must NEVER span across two different semantic sections.
4. **Vectorization**: Batched embedding generation.
5. **Storage**: Simultaneous write to Vector DB (FAISS) and Relational DB (Postgres/Mock). Atomic transactions should be simulated or implemented to prevent orphaned vectors.
