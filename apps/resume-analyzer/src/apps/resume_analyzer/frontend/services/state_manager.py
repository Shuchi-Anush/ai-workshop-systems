import json
import os
import time
from typing import Optional
import streamlit as st
from apps.resume_analyzer.frontend.models.domain import ScreeningSession, CandidateCard, ChatMessage
from apps.resume_analyzer.frontend.utils.constants import SESSION_DIR

class StateManager:
    """Manages lightweight persistence and Streamlit session state."""
    
    @staticmethod
    def init_state():
        if "session" not in st.session_state:
            st.session_state.session = None
            
        os.makedirs(SESSION_DIR, exist_ok=True)
            
    @staticmethod
    def set_active_session(session: ScreeningSession):
        st.session_state.session = session
        StateManager.save_session(session)
        
    @staticmethod
    def get_active_session() -> Optional[ScreeningSession]:
        return st.session_state.get("session")
        
    @staticmethod
    def save_session(session: ScreeningSession):
        file_path = os.path.join(SESSION_DIR, f"{session.session_id}.json")
        try:
            # Simple dict serialization for persistence
            data = {
                "session_id": session.session_id,
                "job_description": session.job_description,
                "shortlisted_ids": session.shortlisted_ids,
                "created_at": session.created_at,
                # Note: CandidateCards are complex, saving raw_data instead to re-hydrate
                "candidates_raw": [c.raw_data for c in session.candidates],
                "chat_history": [{"role": msg.role, "content": msg.content} for msg in session.chat_history]
            }
            with open(file_path, "w") as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Failed to save session: {e}")
            
    @staticmethod
    def load_session(session_id: str) -> Optional[ScreeningSession]:
        file_path = os.path.join(SESSION_DIR, f"{session_id}.json")
        if not os.path.exists(file_path):
            return None
            
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
                
            from apps.resume_analyzer.frontend.services.dto_mapper import DTOMapper
            candidates = DTOMapper.map_candidates(data.get("candidates_raw", []))
            
            chat_history = [ChatMessage(role=m["role"], content=m["content"]) for m in data.get("chat_history", [])]
            
            session = ScreeningSession(
                session_id=data["session_id"],
                job_description=data["job_description"],
                candidates=candidates,
                shortlisted_ids=data.get("shortlisted_ids", []),
                chat_history=chat_history,
                created_at=data.get("created_at", time.time())
            )
            return session
        except Exception as e:
            print(f"Failed to load session: {e}")
            return None
