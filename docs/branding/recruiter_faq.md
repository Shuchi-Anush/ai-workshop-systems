# Recruiter & Hiring Manager FAQ

### 1. "What exactly did you build here?"
I built a production-grade AI Search Engine for resumes. Instead of just wrapping the OpenAI API, I engineered an entirely offline system optimized for 8GB laptops. It uses Vector Databases (ChromaDB) to understand semantic meaning, traditional algorithms (BM25) to ensure exact keyword matching, and custom mathematical formulas to fuse them together.

### 2. "Why is this better than a standard resume parser?"
A standard parser just extracts text. A naive AI search just looks for words that are "close" to the job description. Both are easily tricked if a candidate just copy-pastes 200 technical buzzwords in invisible ink at the bottom of their resume. My platform mathematically detects that "Keyword Stuffing" attack, penalizes it, and ensures only legitimate engineers rise to the top.

### 3. "What was the hardest engineering challenge?"
Defending the system against those adversarial attacks without slowing it down. If I asked a Large Language Model to read every resume to check for cheating, the search would take 20 seconds. That ruins the user experience. I had to drop down to first-principles Information Retrieval. I built a deterministic NLP heuristic that analyzes noun-to-verb grammatical ratios. It catches the cheaters in under 1 millisecond.

### 4. "Why did you build this locally instead of using AWS/GCP?"
To prove deep systems engineering capability. Anyone can spin up an infinite-memory cloud cluster and throw money at latency problems. Constraining myself to a local 8GB offline environment forced me to write highly optimized code. I couldn't use bloated frameworks like LangChain; I had to build the Reciprocal Rank Fusion loop myself to hit my `<50ms` latency SLA. 

### 5. "What role are you targeting?"
I am targeting **Senior/Staff Backend Engineering, AI Systems Architecture, or Machine Learning Infrastructure** roles. I specialize in the layer between the raw Machine Learning model and the production user—Search Quality, RAG scaling, and Operational Resilience.
