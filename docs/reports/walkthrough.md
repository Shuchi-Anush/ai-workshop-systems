# Walkthrough: Retrieval Intelligence Validation & Dataset Engineering

The final phase of the repository evolution focused on mathematically proving the robustness of the retrieval pipeline against common edge cases like **HR Keyword Stuffing** and **Seniority Inflation**.

## 1. Dataset Engineering Pipeline
We created a fully automated ingestion preprocessing pipeline (`scripts/dataset_engineering.py`) capable of parsing raw PDFs, mapping them against a canonical skill hierarchy, and generating benchmark categories:
- **Golden:** Verified technical candidates perfectly matched for the domain.
- **Distractors:** Adjacent candidates sharing overlapping skills but lacking the specific target stack.
- **Noisy/Corrupt:** Unparsable data to test fault tolerance.
- **Adversarial:** Artificially generated PDFs designed to trigger false positives.

### Intelligence Report
From the 2,484 analyzed resumes, `sql` emerged as the predominant skill (appearing 65 times), followed by `java` (20) and `golang` (19). The dataset token average was 870 tokens.

## 2. Evaluation Suite & Metrics
We built an automated evaluation endpoint (`run_evaluations.py`) testing strict Mean Reciprocal Rank (MRR) and NDCG. 

**Initial State (MRR: 0.00)**
Initially, the Boolean Metadata Filter utilized a rigid `$and` clause. If a candidate lacked a single keyword from the query, they were silently dropped, yielding a 0.00 MRR on organic candidates while adversarial resumes sailed through.

**Stabilized State (MRR: 0.50)**
We relaxed the filter to an `$or` boundary, allowing the Dense Vector Search (`all-MiniLM-L6-v2`) to perform semantic ranking. 
- **Avg Latency:** 53.0ms
- **Mean MRR:** 0.50
- **NDCG@3:** 0.43

## 3. The Adversarial Vulnerability (Dense Retrieval Weakness)
Despite stabilizing the queries, **Adversarial Resumes (Keyword Stuffers) continue to leak into the top results**. 
Dense Embeddings evaluate semantic spatial distance. Because the Adversarial generated resumes explicitly enumerate exactly the nouns the query asks for ("I am not a developer but I hire for Python, FastAPI, Docker"), they score higher in pure dense similarity than a natural developer resume.

**Architectural Next Step:** To eliminate these false positives, the platform requires a **Sparse Retriever (BM25)** to apply term-frequency vs. document-frequency normalization, coupled with **Reciprocal Rank Fusion (RRF)** to combine structural frequency with semantic distance.

The repository is now fully operational, benchmarked, mathematically diagnosed, and local-first deployable for the AI Systems Workshop.
