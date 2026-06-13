# The 10-Minute Technical Walkthrough

**Target Audience:** Staff Engineers, Hiring Managers, Technical Interviewers.
**Goal:** Demonstrate deep systems thinking, operational pragmatism, and understanding of RAG scaling bottlenecks.

## Part 1: The Monorepo Architecture (2 mins)
*Open VS Code / Repository Root*
"Before looking at the AI, let's look at the infrastructure. I built this using a `uv` workspace monorepo. Notice the hard boundary between `packages/` and `apps/`. Because this system has to run strictly offline on an 8GB laptop, I explicitly banned microservices. Dockerizing an AI backend and a database separately adds IPC latency and serialization overhead that violates my 50ms retrieval SLA. The monorepo guarantees sub-second dependency resolution while maintaining strict interface isolation."

## Part 2: The Attack Surface (3 mins)
*Open Streamlit Dashboard -> Attack Simulator*
"Most RAG tutorials assume documents are benign. In the HR tech space, they are highly adversarial. I'm going to simulate a 'Keyword Stuffing' attack."
*Run Dense Simulation*
"Notice the latency: ~40ms. But notice the result: Rank #1 is an adversarial payload. Standard embedding models (like the `nomic-embed-text` I'm running locally via Ollama) cluster text based on semantic co-occurrence. A block of 200 technical nouns acts like a gravitational black hole in latent space. It mathematically defeats legitimate resumes. I can't use an LLM to validate this because passing 5 chunks to `phi3` takes 15 seconds. That breaks the SLA."

## Part 3: The Hybrid Defense Pipeline (3 mins)
*Run Hybrid Simulation*
"To fix this without LLMs, I treated it as an Information Retrieval anomaly. I spun up an in-memory BM25 sparse index. BM25 penalizes massive term frequencies if they lack exact query overlap. I built a Reciprocal Rank Fusion pipeline: `1 / (60 + Dense) + 1 / (60 + Sparse)`. I then injected a deterministic NLP heuristic: If the chunk has a high noun-to-verb ratio indicating zero grammar, I multiply the RRF score by `0.1x`. The adversarial resume drops to the bottom instantly."

## Part 4: Explainability & Operations (2 mins)
*Open Streamlit Dashboard -> Education Mode / Live Health*
"Enterprise AI requires explainability. Notice this trace: I don't use LLMs to guess why a resume was retrieved. I do a set intersection of the query tokens against the chunk tokens to prove exact Sparse matches vs semantic Dense matches. Finally, look at the Live Health dashboard. It tracks index synchronization. If ChromaDB corrupts, the system detects the desync against the BM25 pickle and provides a 1-click bootstrap repair script. This platform is operationally hardened to survive a live workshop."
