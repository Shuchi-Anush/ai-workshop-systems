import streamlit as st
from apps.resume_analyzer.frontend.components.layout import set_page_layout, render_sidebar
from apps.resume_analyzer.frontend.services.state_manager import StateManager
from apps.resume_analyzer.frontend.components.candidate_card import render_candidate_card
from apps.resume_analyzer.frontend.models.domain import MatchTier

set_page_layout("Candidates")
render_sidebar()

st.title("Candidate Insights")

session = StateManager.get_active_session()

if not session:
    st.warning("No active screening session. Please create a new screening first.")
    if st.button("Go to New Screening"):
        st.switch_page("pages/02_New_Screening.py")
    st.stop()

if not session.candidates:
    st.info("No candidates evaluated yet for this session.")
    st.stop()

# Filter controls
col1, col2 = st.columns(2)
with col1:
    view_mode = st.radio("View", ["All Evaluated", "Shortlisted Only"], horizontal=True)
with col2:
    tier_filter = st.multiselect("Filter by Tier", [e.value for e in MatchTier], default=[e.value for e in MatchTier])

st.divider()

# Rendering loop
rendered_count = 0
for card in session.candidates:
    is_shortlisted = card.candidate.id in session.shortlisted_ids
    
    if view_mode == "Shortlisted Only" and not is_shortlisted:
        continue
        
    if card.match_tier.value not in tier_filter:
        continue
        
    render_candidate_card(card, is_shortlisted)
    rendered_count += 1

if rendered_count == 0:
    st.info("No candidates match the current filters.")
