import streamlit as st
import os
from apps.resume_analyzer.frontend.components.layout import set_page_layout, render_sidebar
from apps.resume_analyzer.frontend.services.api_client import APIClient
from apps.resume_analyzer.frontend.services.state_manager import StateManager

# Standard Entry Point Setup
set_page_layout("Dashboard")
render_sidebar()

st.title("RecruitAI Overview")
st.markdown("Welcome to the next generation of Talent Intelligence.")

# High level metrics
c1, c2, c3 = st.columns(3)

# System Health Check mapping
health = APIClient.get("/api/v1/health")

if health.get("status") == "ok":
    c1.metric("System Status", "ACTIVE", delta="Online", delta_color="normal")
else:
    c1.metric("System Status", "LOCAL", delta="Degraded", delta_color="off")
    
session = StateManager.get_active_session()

if session:
    c2.metric("Candidates Screened", len(session.candidates))
    c3.metric("Shortlisted", len(session.shortlisted_ids))
    
    st.divider()
    st.markdown("### Active Screening")
    st.info(f"**Session ID:** {session.session_id}")
    st.markdown("**Job Description Segment:**")
    st.caption(session.job_description[:200] + "..." if len(session.job_description) > 200 else session.job_description)
    
    colA, colB = st.columns(2)
    with colA:
        if st.button("Resume Screening", use_container_width=True, type="primary"):
            st.switch_page("pages/03_Candidates.py")
    with colB:
        if st.button("Chat with AI Assistant", use_container_width=True):
            st.switch_page("pages/04_AI_Assistant.py")
else:
    c2.metric("Candidates Screened", 0)
    c3.metric("Shortlisted", 0)
    
    st.divider()
    st.markdown("### No Active Session")
    st.info("Start a new screening session to begin importing candidates and evaluating resumes.")
    
    if st.button("Create New Screening", type="primary", use_container_width=True):
        st.switch_page("pages/02_New_Screening.py")
