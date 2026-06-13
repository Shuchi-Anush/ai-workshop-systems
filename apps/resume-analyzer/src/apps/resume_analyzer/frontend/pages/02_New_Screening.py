import streamlit as st
import time
from apps.resume_analyzer.frontend.components.layout import set_page_layout, render_sidebar
from apps.resume_analyzer.frontend.services.session_service import SessionService
from apps.resume_analyzer.frontend.services.ranking_service import RankingService
from apps.resume_analyzer.frontend.services.state_manager import StateManager

set_page_layout("New Screening")
render_sidebar()

st.title("Create New Screening")

# Wizard Progress
progress = st.progress(0, text="Step 1: Define Job Requirements")

st.markdown("### Step 1: Upload Candidate Resumes")
st.info("In this local deployment mode, resumes are processed securely from the backend `.data/` directory. Simulating upload connection to internal repository...")
uploaded_files = st.file_uploader("Upload Resumes (PDF, DOCX)", accept_multiple_files=True)

st.divider()
st.markdown("### Step 2: Define Job Description")
job_description = st.text_area("Paste the Job Description or Required Skills", height=200, placeholder="e.g. Senior Python Developer with FastAPI, Docker, and Kubernetes experience...")

st.divider()
if st.button("Start AI Analysis", type="primary", use_container_width=True, disabled=len(job_description) < 10):
    progress.progress(25, text="Step 2: Initializing Screening Session")
    session = SessionService.create_new_session()
    session.job_description = job_description
    
    progress.progress(35, text="Step 2b: Uploading Resumes")
    if uploaded_files:
        files_to_upload = [("files", (f.name, f.getvalue(), f.type)) for f in uploaded_files]
        from apps.resume_analyzer.frontend.services.api_client import APIClient
        APIClient.upload_files("/api/v1/upload-resumes", data={"session_id": session.session_id}, files=files_to_upload)
    
    progress.progress(50, text="Step 3: AI Vector Matching & Analysis")
    # Execute backend ranking using the session endpoint
    candidates = RankingService.evaluate_candidates(session.session_id, job_description)
    
    if candidates is None:
        st.error("Failed to evaluate candidates. Please check backend connection.")
        progress.progress(0, text="Failed")
    else:
        progress.progress(80, text="Step 4: Compiling Profiles")
        session.candidates = candidates
        StateManager.save_session(session)
        progress.progress(100, text="Complete!")
        time.sleep(0.5)
        st.success("Screening Complete! Redirecting to Candidate View...")
        time.sleep(0.5)
        st.switch_page("pages/03_Candidates.py")
