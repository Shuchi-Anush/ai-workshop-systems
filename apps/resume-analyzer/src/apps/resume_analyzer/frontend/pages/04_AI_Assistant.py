import streamlit as st
from apps.resume_analyzer.frontend.components.layout import set_page_layout, render_sidebar
from apps.resume_analyzer.frontend.services.state_manager import StateManager
from apps.resume_analyzer.frontend.services.rag_service import RAGService
from apps.resume_analyzer.frontend.models.domain import ChatMessage

set_page_layout("AI Assistant")
render_sidebar()

st.title("AI Recruitment Assistant")

session = StateManager.get_active_session()

if not session:
    st.warning("No active screening session. The assistant needs a session context.")
    st.stop()

st.markdown(f"**Chat Context:** {len(session.shortlisted_ids)} shortlisted candidates.")
st.divider()

# Render chat history
for msg in session.chat_history:
    with st.chat_message(msg.role):
        st.markdown(msg.content)

# Chat input
if prompt := st.chat_input("Ask about the shortlisted candidates... e.g. 'Who has the most cloud experience?'"):
    # Add user message
    user_msg = ChatMessage(role="user", content=prompt)
    session.chat_history.append(user_msg)
    
    with st.chat_message("user"):
        st.markdown(prompt)
        
    # Generate AI response
    with st.chat_message("assistant"):
        with st.spinner("Analyzing candidates..."):
            ai_response_text = RAGService.ask_assistant(session.session_id, prompt, session.shortlisted_ids)
            st.markdown(ai_response_text)
            
    # Save assistant message
    ai_msg = ChatMessage(role="assistant", content=ai_response_text)
    session.chat_history.append(ai_msg)
    StateManager.save_session(session)
