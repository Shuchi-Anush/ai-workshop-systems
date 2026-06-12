# Ranking Pipeline

Unlike standard document QA, Resume RAG requires candidate-level synthesis.

1. **Aggregation**: The `ICandidateAggregator` groups the disparate retrieved chunks by `candidate_id`.
2. **Heuristic Scoring (`IRanker`)**: 
   * A candidate's base score is derived from the aggregated vector similarity scores of their matched chunks.
   * Modifiers are applied based on metadata (e.g., matched chunks in "Experience" section weigh more than "Hobbies").
3. **Sorting**: Candidates are ranked descending by final score.
