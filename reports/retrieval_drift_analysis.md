# Retrieval Drift Analysis

## Overview
Retrieval drift occurs when the ranking order of documents fluctuates significantly depending on the retrieval method (Dense vs Sparse) or when adversarial candidates disrupt the space.

## Volatility and Consistency
Based on our multi-mode benchmark (`tests/retrieval_benchmarks/run_evaluations.py`):

1. **Dense Retrieval Drift**
   - High sensitivity to adversarial documents. `adv_hr_keyword_stuffed` consistently drifts into the Top 3 because the Dense embedder maps the high volume of semantic keywords into a dense area of the latent space, regardless of syntax.
   
2. **Sparse Retrieval (BM25) Consistency**
   - Highly stable for exact matches (e.g., "FastAPI", "Docker").
   - Severe drift when the query uses synonyms or conceptual requests. (e.g., "Frontend Developer" misses resumes that only say "React Engineer" unless exact words overlap).

3. **Hybrid RRF Stability**
   - Hybrid ranking stabilizes the drift. By enforcing `k=60` in the Reciprocal Rank Fusion, a candidate must perform reasonably well in both spaces to reach Top 3.
   - However, the `React Frontend Developer with JavaScript` query still resulted in 0.00 MRR across all modes, indicating that when both Dense and Sparse miss the semantic connection simultaneously, the RRF score collapses.

## Adversarial Sensitivity
- The Adversarial Penalty multiplier (currently `0.1x`) successfully punishes obvious noun-stacking. 
- However, "Seniority Inflation" (e.g., `adv_fake_seniority`) is immune to keyword density checks because it uses grammatically correct sentences to lie. This causes Dense drift where junior resumes overtake senior resumes simply by asserting seniority.

## Conclusion
Hybrid retrieval prevents pure keyword-stuffing drift but is still vulnerable to sophisticated semantic inflation. Next steps involve stricter metadata filtering enforcement before the ranking phase.
