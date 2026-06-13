# Final Retrieval Quality Assessment

> [!IMPORTANT]
> This report documents the final baseline benchmark metrics for the local-first Resume Intelligence System following the Phase 5 infrastructure stabilization.

## 1. Aggregate Benchmark Metrics

After engineering a reproducible benchmark subset of resumes spanning Golden, Distractor, and Adversarial categories, the evaluation suite (`run_evaluations.py`) yielded the following metrics over a 27-resume evaluation pool (61 semantic chunks):

- **Mean Reciprocal Rank (MRR):** 0.50
- **Precision at 3 (P@3):** 0.44
- **Recall at 3 (R@3):** 0.23
- **NDCG@3:** 0.43
- **Average Query Latency:** 53.0ms
- **Total False Positives:** 3 (Adversarial Leaks)

### Query-Level Breakdown

| Query | Expected Target | MRR | P@3 | R@3 | NDCG@3 | False Positive Penetration |
|-------|-----------------|-----|-----|-----|--------|----------------------------|
| Senior Python Developer with FastAPI and Docker | Golden Python Candidates | 0.50 | 0.33 | 0.20 | 0.30 | Rank 1 (`adv_fake_seniority`), Rank 3 (`adv_hr_keyword_stuffed`) |
| React Frontend Developer with JavaScript | Distractor React Candidates | 0.00 | 0.00 | 0.00 | 0.00 | Rank 1 (`adv_fake_seniority`), Rank 2 (`adv_hr_keyword_stuffed`) |
| Senior C# Backend Engineer .NET Core | Distractor C# Candidates | 1.00 | 1.00 | 0.50 | 1.00 | None |

---

## 2. Known Retrieval Weaknesses

> [!WARNING]
> The current system relies on Metadata-Filtered Dense Retrieval (ChromaDB `all-MiniLM-L6-v2`). This architecture is mathematically vulnerable to **Keyword Stuffing** and **Adversarial Resumes**.

### 2.1 Adversarial Bleed-Through
As proven by the benchmark, adversarial resumes explicitly injected with excessive target keywords (e.g., "I hire for Python, FastAPI, Docker, Kubernetes, React, C#, Java") consistently out-rank genuine technical candidates. 
- **Why it happens:** Dense embeddings map queries like "Python Developer with FastAPI and Docker" to regions heavily influenced by the literal presence of those tokens. The adversarial text maximizes semantic overlap by containing all target nouns, pushing it closer in vector space than a natural candidate resume that discusses those tools organically.

### 2.2 Lack of Sparse Term-Frequency Analysis
The system lacks a sparse BM25 retriever. BM25 evaluates Term Frequency vs. Inverse Document Frequency (TF-IDF). While BM25 is also sensitive to keywords, a mature hybrid search with Reciprocal Rank Fusion (RRF) and proper length normalization (BM25 `b` parameter) would penalize short, stuffed resumes and reward dense, naturally distributed contexts.

### 2.3 Boolean Filter Rigidity
Initially, the Boolean Metadata Filter operated as a strict `$and` clause. If a candidate lacked even one explicit skill from the query, they were silently dropped before vector search. 
- **Fix Applied:** Relaxed the filter to `$or` to guarantee high recall, deferring to the vector similarity for precision ranking. 
- **Tradeoff:** This increased recall from 0.00 to 0.50 MRR, but allowed keyword-stuffed HR resumes (which pass the `$or` filter due to matched keywords) to dominate the top ranks.

---

## 3. Workshop Production Strategy & Next Steps

For the upcoming local-first AI workshop, the current architecture is stable, scalable, and fully deterministic. However, to achieve production-grade retrieval:

1. **Introduce Sparse Retrieval (BM25):** Maintain a local BM25 index alongside ChromaDB.
2. **Implement Reciprocal Rank Fusion (RRF):** Combine the Vector Similarity score with the BM25 TF-IDF score.
3. **LLM-Based Re-ranking (Optional but Heavy):** Use a local cross-encoder or the existing `phi3` LLM to re-rank the top 10 candidates based on a strict prompt ("Is this candidate actually an engineer or an HR manager?").

The baseline platform is now structurally sound, latency-safe, and ready for workshop deployment.
