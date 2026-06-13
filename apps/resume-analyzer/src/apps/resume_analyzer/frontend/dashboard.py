import streamlit as st
import requests
import json
import pandas as pd
import time
import os

API_URL = "http://127.0.0.1:8081"

st.set_page_config(page_title="AI Resume Intelligence Showcase", layout="wide", page_icon="🔭")

# -- Helper Functions --
def api_get(endpoint):
    try:
        return requests.get(f"{API_URL}{endpoint}").json()
    except Exception as e:
        return {"status": "error", "message": str(e)}

def api_post(endpoint, payload):
    try:
        return requests.post(f"{API_URL}{endpoint}", json=payload).json()
    except Exception as e:
        return {"status": "error", "message": str(e)}

def render_explainability(explain_data):
    if not explain_data: return
    st.markdown("#### 🧠 Explainability Trace")
    c1, c2, c3 = st.columns(3)
    c1.metric("Dense Score", f"{explain_data.get('rrf_contribution', {}).get('dense', 0.0):.4f}")
    c2.metric("Sparse (BM25) Score", f"{explain_data.get('rrf_contribution', {}).get('bm25', 0.0):.4f}")
    
    pen = explain_data.get("adversarial_penalty", 1.0)
    c3.metric("Adversarial Penalty", f"{pen}x", delta="Clean" if pen==1.0 else "Flagged", delta_color="normal" if pen==1.0 else "inverse")
    
    st.write("**Matched Sparse Terms:**", ", ".join(explain_data.get("matched_sparse_terms", [])) or "None")
    st.write("**Matched Dense Concepts:**", ", ".join(explain_data.get("matched_dense_concepts", [])) or "None")
    st.write("**Path:**", " ➡️ ".join(explain_data.get("retrieval_path", [])))

def render_candidate_card(rank, c):
    cand = c.get("candidate", {})
    diag = c.get("diagnostics", {})
    explain = diag.get("explainability", {})
    cid = cand.get('candidate_id', 'Unknown')
    
    with st.container():
        st.markdown(f"### 🏅 Rank #{rank} - {cid}")
        c1, c2 = st.columns([1, 2])
        with c1:
            st.metric("Final Fusion Score", f"{c.get('score', 0):.4f}")
            st.metric("Dense Rank", diag.get("dense_rank", "N/A"))
            st.metric("BM25 Rank", diag.get("bm25_rank", "N/A"))
        with c2:
            render_explainability(explain)
        st.divider()

# -- UI Setup --
st.sidebar.title("🔭 Platform Operations")
app_mode = st.sidebar.radio("Navigation", [
    "🚀 1-Click Executive Demo",
    "🔍 Retrieval Visualization",
    "⚔️ Attack Simulator",
    "📦 Chunk Intelligence",
    "🎓 Education Mode",
    "⚕️ Live Health & Leaderboard"
])

st.sidebar.markdown("---")
st.sidebar.caption("AI Workshop Systems Platform v2.0")

if app_mode == "🚀 1-Click Executive Demo":
    st.title("🚀 1-Click Executive Demo Scenario Runner")
    st.markdown("Instantly showcase the hybrid retrieval's ability to resist manipulation and understand context.")
    
    scenarios = {
        "1. Naive Dense Failure (Adversarial)": {
            "query": "Senior Python Developer with FastAPI and Docker",
            "mode": "dense",
            "desc": "Dense retrieval fails to detect syntax-less keyword stuffing, pulling adversarial resumes to the top."
        },
        "2. Sparse Retrieval Failure (Synonyms)": {
            "query": "React Frontend Developer with JavaScript",
            "mode": "sparse",
            "desc": "Sparse retrieval (BM25) fails when exact keywords don't match, causing zero recall on valid semantic matches."
        },
        "3. Hybrid Retrieval Stabilization": {
            "query": "Senior C# Backend Engineer .NET Core",
            "mode": "hybrid",
            "desc": "Hybrid search (RRF) successfully balances exact term matching with semantic concepts, pushing adversaries down."
        }
    }
    
    selected_scenario = st.selectbox("Select Scenario", list(scenarios.keys()))
    scenario = scenarios[selected_scenario]
    
    st.info(f"**Objective:** {scenario['desc']}")
    
    if st.button("▶️ Execute Scenario"):
        with st.spinner("Executing Scenario..."):
            res = api_post("/api/v1/evaluate", {"job_description": scenario["query"], "top_k": 3, "mode": scenario["mode"]})
            st.success(f"Execution complete in {res.get('execution_time_ms', 0):.1f} ms")
            for rank, c in enumerate(res.get("candidates", []), 1):
                render_candidate_card(rank, c)

elif app_mode == "🔍 Retrieval Visualization":
    st.title("🔍 Retrieval Flow & Visualization Engine")
    st.markdown("Interact directly with the search pipeline across Dense, Sparse, and Hybrid spaces.")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        query = st.text_input("Search Query:", value="Senior Python Developer with FastAPI and Docker")
    with col2:
        mode = st.selectbox("Retrieval Mode", ["hybrid", "dense", "sparse"])
        
    if st.button("Run Deep Diagnostics"):
        with st.spinner("Executing Pipeline..."):
            res = api_post("/api/v1/evaluate", {"job_description": query, "top_k": 3, "mode": mode})
            
            st.markdown("### 🌊 Pipeline Flow")
            cols = st.columns(6)
            cols[0].info("1. Query")
            cols[1].success("2. Extraction")
            cols[2].warning("3. Dense/Sparse Search")
            cols[3].error("4. RRF Fusion")
            cols[4].info("5. Adversarial Penalty")
            cols[5].success("6. Final Ranking")
            
            st.markdown("### 🏆 Top Results")
            for rank, c in enumerate(res.get("candidates", []), 1):
                render_candidate_card(rank, c)
                
            if st.checkbox("Show Vector-vs-BM25 Comparison Data"):
                st.write("Score Comparisons:")
                data = []
                for c in res.get("candidates", []):
                    d = c.get("diagnostics", {})
                    data.append({
                        "Candidate": c.get("candidate", {}).get("candidate_id"),
                        "Dense Rank": d.get("dense_rank", 100),
                        "BM25 Rank": d.get("bm25_rank", 100),
                        "RRF": d.get("rrf_score", 0)
                    })
                st.dataframe(pd.DataFrame(data), use_container_width=True)

elif app_mode == "⚔️ Attack Simulator":
    st.title("⚔️ Adversarial Attack Simulator")
    st.markdown("Inject keyword stuffing and seniority inflation to see how retrieval algorithms react.")
    
    st.warning("This simulates querying a vector space contaminated with adversarial resumes.")
    
    query = st.text_input("Target Job Query:", value="Senior Data Engineer PySpark")
    
    colA, colB = st.columns(2)
    with colA:
        if st.button("Simulate Dense-Only (Vulnerable)"):
            with st.spinner("Attacking Dense Space..."):
                res = api_post("/api/v1/evaluate", {"job_description": query, "top_k": 3, "mode": "dense"})
                for rank, c in enumerate(res.get("candidates", []), 1):
                    cand_id = c.get("candidate", {}).get("candidate_id", "")
                    if "adv_" in cand_id:
                        st.error(f"#{rank} - {cand_id} (ADVERSARIAL LEAK!)")
                    else:
                        st.success(f"#{rank} - {cand_id} (Clean)")
    with colB:
        if st.button("Simulate Hybrid (Protected)"):
            with st.spinner("Defending via Hybrid RRF..."):
                res = api_post("/api/v1/evaluate", {"job_description": query, "top_k": 3, "mode": "hybrid"})
                for rank, c in enumerate(res.get("candidates", []), 1):
                    cand_id = c.get("candidate", {}).get("candidate_id", "")
                    if "adv_" in cand_id:
                        st.error(f"#{rank} - {cand_id} (ADVERSARIAL LEAK!)")
                    else:
                        st.success(f"#{rank} - {cand_id} (Clean)")

elif app_mode == "📦 Chunk Intelligence":
    st.title("📦 Chunk Intelligence Explorer")
    st.markdown("Visualizing chunking impact on retrieval mathematics.")
    
    st.info("Current chunking strategy: Rule-based boundary splits (Experience vs Skills)")
    
    c1, c2 = st.columns(2)
    c1.metric("Average Chunk Length", "~1045 chars")
    c2.metric("Max Chunk Length", "4192 chars (Semantic Dilution Risk)")
    
    st.markdown("### Semantic Dilution Demonstration")
    st.write("When highly dense skill sections are bundled with verbose experience points, BM25 term frequency drops. Adversaries exploit this by keeping chunk length small and keyword frequency high.")
    
    st.markdown("### The Solution Roadmap")
    st.markdown("- **Sliding Window:** Overlap chunks by 200 characters to prevent context loss.")
    st.markdown("- **Metadata Segregation:** Remove skills from vector search entirely and treat them as exact-match boolean filters.")

elif app_mode == "🎓 Education Mode":
    st.title("🎓 Learn Hybrid Search Architecture")
    
    st.markdown("""
    ### Why Local Hybrid Retrieval?
    
    **1. Dense Embeddings (ChromaDB + Nomic)**
    - **Pros:** Understands semantic concepts ("Frontend" ~= "React").
    - **Cons:** Easily manipulated by Keyword Stuffing. Syntactically broken lists of words clump together in latent space.
    
    **2. Sparse Retrieval (BM25)**
    - **Pros:** Exact keyword matching. High term frequency forces relevance.
    - **Cons:** Vocabulary mismatch problem. Fails on synonyms.
    
    **3. Reciprocal Rank Fusion (RRF)**
    - Combines ranks, not raw scores.
    - Formula: `1 / (k + rank)`
    - Forces a candidate to perform well in BOTH spaces to reach the top.
    
    **4. Adversarial Defense Pipeline**
    - Scans retrieved text for high keyword density and low semantic diversity.
    - Applies a `0.1x` penalty multiplier to the final RRF score, burying fake resumes.
    """)

elif app_mode == "⚕️ Live Health & Leaderboard":
    st.title("⚕️ Platform Operations & Metrics")
    
    health_tab, lb_tab = st.tabs(["Live Health", "Benchmark Leaderboard"])
    
    with health_tab:
        if st.button("Refresh Health State"):
            with st.spinner("Pinging API..."):
                health = api_get("/api/v1/health")
                models = api_get("/api/v1/health/models")
                indexes = api_get("/api/v1/health/indexes")
                
                c1, c2, c3 = st.columns(3)
                c1.metric("API Status", health.get("status", "error").upper())
                c2.metric("Ollama Models", "READY" if models.get("phi3_available") and models.get("nomic_available") else "MISSING")
                c3.metric("Index Sync", "SYNCED" if indexes.get("synced") else "DESYNCED")
                
                st.markdown("### Detailed Diagnostics")
                st.json({"health": health, "models": models, "indexes": indexes})

    with lb_tab:
        if os.path.exists("reports/retrieval_leaderboard.json"):
            with open("reports/retrieval_leaderboard.json", "r") as f:
                lb = json.load(f)
            df = pd.DataFrame(lb).T
            st.dataframe(df, use_container_width=True)
            
            st.bar_chart(df[["Mean MRR", "Mean R@3"]])
        else:
            st.warning("Run tests/retrieval_benchmarks/run_evaluations.py first.")
