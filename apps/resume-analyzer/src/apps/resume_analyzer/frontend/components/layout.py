import streamlit as st
from apps.resume_analyzer.frontend.config.theme import apply_enterprise_theme
from apps.resume_analyzer.frontend.services.state_manager import StateManager

def set_page_layout(title: str):
    """Sets standard page configuration and layout."""
    st.set_page_config(
        page_title=f"{title} | RecruitAI Enterprise", 
        layout="wide", 
        page_icon="💼",
        initial_sidebar_state="expanded"
    )
    apply_enterprise_theme()
    StateManager.init_state()

def render_sidebar():
    """Renders the standard enterprise sidebar."""
    st.sidebar.markdown("## RecruitAI Enterprise")
    st.sidebar.caption("AI-Powered Talent Intelligence")
    st.sidebar.divider()
    
    st.sidebar.page_link("app.py", label="Dashboard", icon="📊")
    st.sidebar.page_link("pages/02_New_Screening.py", label="New Screening", icon="➕")
    st.sidebar.page_link("pages/03_Candidates.py", label="Candidates", icon="👥")
    st.sidebar.page_link("pages/04_AI_Assistant.py", label="AI Assistant", icon="💬")
    st.sidebar.page_link("pages/05_Reports.py", label="Reports", icon="📈")
    
    st.sidebar.divider()
    session = StateManager.get_active_session()
    if session:
        st.sidebar.info(f"**Active Session:**\n{session.session_id}\n\n**Shortlisted:** {len(session.shortlisted_ids)}")
    else:
        st.sidebar.warning("No active session.")
        
    # Hidden Technical Mode
    if st.query_params.get("mode") == "admin":
        st.sidebar.divider()
        st.sidebar.markdown("### Engineering Operations")
        st.sidebar.page_link("pages/99_Technical_Insights.py", label="Technical Insights", icon="⚙️")
