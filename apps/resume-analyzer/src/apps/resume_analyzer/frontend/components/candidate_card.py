import streamlit as st
from apps.resume_analyzer.frontend.models.domain import CandidateCard, MatchTier
from apps.resume_analyzer.frontend.services.session_service import SessionService

def render_candidate_card(card: CandidateCard, is_shortlisted: bool = False):
    """Renders a modern, SaaS-style candidate card."""
    with st.container():
        st.markdown(f"<div class='candidate-card'>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            st.markdown(f"### {card.candidate.name}")
            st.caption(f"ID: {card.candidate.id}")
            
            st.markdown("**Top Skills:**")
            skills_html = "".join([f"<span class='skill-chip'>{s}</span>" for s in card.candidate.skills[:5]])
            if not skills_html:
                skills_html = "<span class='skill-chip'>No skills parsed</span>"
            st.markdown(skills_html, unsafe_allow_html=True)
            
        with col2:
            # Match Badge
            badge_class = "match-badge-high"
            if card.match_tier == MatchTier.MEDIUM:
                badge_class = "match-badge-med"
            elif card.match_tier in (MatchTier.LOW, MatchTier.POOR):
                badge_class = "match-badge-low"
                
            st.markdown(f"<div class='{badge_class}' style='text-align: center;'>{card.match_score_percent}% Match<br><small>{card.match_tier.value}</small></div>", unsafe_allow_html=True)
            
            # Flags
            if card.flags:
                for flag in card.flags:
                    st.error(flag)
                    
        with col3:
            st.write("") # Spacing
            if st.button("⭐ Shortlist" if not is_shortlisted else "Remove", key=f"shortlist_{card.candidate.id}", use_container_width=True):
                SessionService.toggle_shortlist(card.candidate.id)
                st.rerun()
                
            with st.popover("View Details", use_container_width=True):
                st.markdown(f"**Experience:**\n{card.candidate.experience}")
                st.divider()
                st.markdown(f"**Education:**\n{card.candidate.education}")
                
                if card.strengths:
                    st.divider()
                    st.markdown("**AI Identified Strengths:**")
                    for s in card.strengths:
                        st.markdown(f"- {s}")
                        
        st.markdown("</div>", unsafe_allow_html=True)
