# Task 01: Resume RAG Pipeline

**Status**: Architecture Stabilization Phase.

**Overview**: A specialized Retrieval-Augmented Generation system designed for semantic candidate-job matching.

**Key Differentiators from Standard RAG**:
* Semantic chunking over naive character splitting.
* Candidate-level aggregation post-retrieval.
* Heuristic ranking applied on top of vector similarity.

**Current Focus**: Formalizing interface boundaries and establishing deterministic ingestion.
