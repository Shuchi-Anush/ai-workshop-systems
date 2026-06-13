import streamlit as st
import json
import pandas as pd
import os
from apps.resume_analyzer.frontend.components.layout import set_page_layout, render_sidebar
from apps.resume_analyzer.frontend.services.api_client import APIClient
from apps.resume_analyzer.frontend.services.state_manager import StateManager

set_page_layout("Technical Insights")
render_sidebar()

st.title("⚙️ Engineering Operations & Insights")
st.warning("RESTRICTED AREA. This page exposes raw ML pipelines, adversarial defenses, and infrastructure metrics.")

if st.query_params.get("mode") != "admin":
    st.error("Access Denied. You must append `?mode=admin` to the URL to view this page.")
    st.stop()

health_tab, lb_tab, diag_tab = st.tabs(["System Health", "Retrieval Leaderboard", "Raw Candidate Vectors"])

with health_tab:
    if st.button("Refresh Infrastructure State"):
        with st.spinner("Pinging API..."):
            health = APIClient.get("/api/v1/health")
            models = APIClient.get("/api/v1/health/models")
            indexes = APIClient.get("/api/v1/health/indexes")
            
            c1, c2, c3 = st.columns(3)
            c1.metric("API Status", health.get("status", "error").upper())
            c2.metric("Ollama Models", "READY" if models.get("phi3_available") and models.get("nomic_available") else "MISSING")
            c3.metric("Index Sync", "SYNCED" if indexes.get("synced") else "DESYNCED")
            
            with st.expander("View Raw Diagnostics Dumps"):
                st.json({"health": health, "models": models, "indexes": indexes})

with lb_tab:
    st.markdown("### Pre-calculated Benchmark Leaderboard")
    if os.path.exists("reports/retrieval_leaderboard.json"):
        with open("reports/retrieval_leaderboard.json", "r") as f:
            lb = json.load(f)
        df = pd.DataFrame(lb).T
        st.dataframe(df, use_container_width=True)
        st.bar_chart(df[["Mean MRR", "Mean R@3"]])
    else:
        st.warning("Leaderboard missing. Run benchmarks via terminal.")

with diag_tab:
    session = StateManager.get_active_session()
    if session and session.candidates:
        st.markdown(f"Raw Vector Outputs for Session: `{session.session_id}`")
        for card in session.candidates:
            with st.expander(f"{card.candidate.name} [{card.candidate.id}]"):
                diag = card.raw_data.get("diagnostics", {})
                st.write("**RRF Score:**", diag.get("rrf_score"))
                st.write("**Dense Rank:**", diag.get("dense_rank"))
                st.write("**BM25 Rank:**", diag.get("bm25_rank"))
                st.json(card.raw_data.get("diagnostics", {}))
    else:
        st.info("No candidates evaluated in the current session.")
