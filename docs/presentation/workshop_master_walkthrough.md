# The Master Demo Walkthrough
*This is the official script for presenting the AI Resume Intelligence Platform during workshops or executive reviews.*

## PRE-FLIGHT CHECK
Before presenting, ensure the environment is certified:
1. Run `uv run python apps/resume-analyzer/scripts/bootstrap_workshop.py`
2. Start API: `uv run uvicorn apps.resume_analyzer.backend.api.main:app --port 8081 --workers 1`
3. Start Dashboard: `uv run streamlit run apps/resume-analyzer/src/apps/resume_analyzer/frontend/dashboard.py`

---

## SCENE 1: The Promise vs The Reality
**Visual:** Open the `1-Click Executive Demo` tab on the Dashboard.

**Speaker Track:**
"Everyone is building RAG applications right now. The standard architecture is simple: Take documents, embed them into a Vector Database, and run a cosine similarity search against user queries. Let me show you why that fails in production."

**Action:** Select Scenario 1: `Naive Dense Failure` and click **Execute**.

**Speaker Track:**
"I've searched for a 'Senior Python Developer'. The system returned a candidate. But look closely at the Resume ID. It's an *Adversarial Document*. This resume isn't a real person; it's just a block of 200 technical buzzwords with zero grammar. Because Vector databases cluster words by semantic co-occurrence, a massive block of jargon acts like a mathematical black hole. It sits perfectly in the center of the latent space, dragging the query to it and completely overriding legitimate resumes. This is Semantic Contamination."

---

## SCENE 2: The Fallback that Fails
**Action:** Switch to Scenario 2: `Sparse Retrieval Failure`. Click **Execute**.

**Speaker Track:**
"If vectors are vulnerable, why not just use traditional keyword search like Elasticsearch's BM25? Look at this query: 'React Frontend Developer with JavaScript'. The BM25 algorithm scored a 0. Why? Because the legitimate resumes in our database wrote 'UI Engineer' or didn't explicitly use the exact string 'JavaScript'. BM25 suffers from the Vocabulary Mismatch problem. It has zero semantic understanding."

---

## SCENE 3: The Hybrid Stabilization
**Action:** Switch to Scenario 3: `Hybrid Retrieval Stabilization`. Click **Execute**.

**Speaker Track:**
"Here is the solution: Reciprocal Rank Fusion (RRF). We don't choose between Dense and Sparse; we fuse them. By calculating `1 / (60 + Dense Rank) + 1 / (60 + Sparse Rank)`, we force a candidate to prove they belong in *both* spaces."

**Visual:** Open the Explainability Trace in the candidate card.

**Speaker Track:**
"Look at this deterministic trace. The system shows exactly which words triggered the BM25 index and which metadata triggered the Vector index. And notice the Adversarial Penalty Multiplier? Our heuristic pipeline detected the grammar-less keyword-stuffed resume from Scene 1, applied a `0.1x` penalty to its RRF score, and mathematically buried it. All running locally, completely offline, in under 50 milliseconds."

---

## SCENE 4: The Deep Dive
**Visual:** Open the `Chunk Intelligence Explorer` tab.

**Speaker Track:**
"To achieve this, we had to rethink chunking. A massive contiguous block of text dilutes BM25 term frequency. By intelligently overlapping boundaries, we maintain high keyword density without losing semantic context."

**Conclusion:**
"This isn't an OpenAI API wrapper. This is a production-grade, adversarial-resistant Information Retrieval platform built for strict memory constraints."
