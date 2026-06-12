# Retrieval Evaluation Framework

To transition from prototype to production, retrieval quality must be measurable. This framework defines the offline evaluation strategy.

## Evaluation Dataset Strategy
* We must curate a golden dataset of (Job Description, Candidate Resumes, Relevance Judgments).
* Relevance Judgments will be binary (Relevant / Not Relevant) or graded (0-3 scale).

## Benchmark Methodology
* **Offline Evaluation Workflows**: CI/CD pipelines will run an evaluation suite whenever embedding models, chunking strategies, or ranking heuristics are modified.
* **Metrics**:
  * **Retrieval Metrics (Chunk Level)**: Recall@K, Mean Reciprocal Rank (MRR).
  * **Ranking Metrics (Candidate Level)**: nDCG (Normalized Discounted Cumulative Gain), Precision@K.

## Automation
* The system will include a dedicated `scripts/evaluate_retrieval.py` tool.
* Embedding comparisons (e.g., testing `all-MiniLM-L6-v2` against `bge-large-en`) must be completely automated using the interface contracts.
