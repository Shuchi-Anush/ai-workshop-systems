import time
import uuid
from typing import Optional
from apps.resume_analyzer.frontend.models.domain import ScreeningSession
from apps.resume_analyzer.frontend.services.state_manager import StateManager

class SessionService:
    """Manages creation and lifecycle of recruiter screening sessions."""
    
    @staticmethod
    def create_new_session() -> ScreeningSession:
        from apps.resume_analyzer.frontend.services.api_client import APIClient
        res = APIClient.post("/api/v1/sessions/create", {})
        session_id = res.get("session_id", f"session_{uuid.uuid4().hex[:8]}")
        session = ScreeningSession(
            session_id=session_id,
            job_description="",
            created_at=time.time()
        )
        StateManager.set_active_session(session)
        return session
        
    @staticmethod
    def toggle_shortlist(candidate_id: str):
        session = StateManager.get_active_session()
        if not session:
            return
            
        if candidate_id in session.shortlisted_ids:
            session.shortlisted_ids.remove(candidate_id)
        else:
            session.shortlisted_ids.append(candidate_id)
            
        from apps.resume_analyzer.frontend.services.api_client import APIClient
        APIClient.post(f"/api/v1/sessions/{session.session_id}/shortlist/{candidate_id}", {})
            
        StateManager.save_session(session)
