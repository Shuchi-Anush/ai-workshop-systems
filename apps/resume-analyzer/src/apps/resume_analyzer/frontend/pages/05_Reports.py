import streamlit as st
import pandas as pd
from apps.resume_analyzer.frontend.components.layout import set_page_layout, render_sidebar
from apps.resume_analyzer.frontend.services.state_manager import StateManager

set_page_layout("Reports")
render_sidebar()

st.title("Export & Reports")

session = StateManager.get_active_session()

if not session:
    st.warning("No active session.")
    st.stop()

if not session.shortlisted_ids:
    st.info("No candidates have been shortlisted yet. Please review and shortlist candidates to generate a report.")
    st.stop()

st.markdown(f"### Export Shortlisted Candidates ({len(session.shortlisted_ids)})")

# Build report data
report_data = []
for card in session.candidates:
    if card.candidate.id in session.shortlisted_ids:
        report_data.append({
            "Candidate ID": card.candidate.id,
            "Name": card.candidate.name,
            "Match Percentage": card.match_score_percent,
            "Tier": card.match_tier.value,
            "Flags": ", ".join(card.flags) if card.flags else "Clean"
        })

df = pd.DataFrame(report_data)

st.dataframe(df, use_container_width=True)

csv = df.to_csv(index=False).encode('utf-8')

st.download_button(
    label="Download CSV Report",
    data=csv,
    file_name=f'recruit_ai_shortlist_{session.session_id}.csv',
    mime='text/csv',
    type="primary"
)
