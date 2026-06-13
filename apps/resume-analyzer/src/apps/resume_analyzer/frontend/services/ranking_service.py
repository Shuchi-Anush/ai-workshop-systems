from typing import List, Optional
from apps.resume_analyzer.frontend.services.api_client import APIClient
from apps.resume_analyzer.frontend.services.dto_mapper import DTOMapper
from apps.resume_analyzer.frontend.models.domain import CandidateCard
from apps.resume_analyzer.frontend.utils.validators import validate_evaluation_response

class RankingService:
    """Handles communication with the backend evaluation APIs."""
    
    @staticmethod
    def evaluate_candidates(session_id: str, job_description: str, top_k: int = 5) -> Optional[List[CandidateCard]]:
        payload = {
            "job_description": job_description,
            "top_k": top_k,
            "mode": "hybrid" # Always use hybrid for the recruiter view
        }
        
        response = APIClient.post(f"/api/v1/sessions/{session_id}/evaluate", payload)
        
        if not validate_evaluation_response(response):
            return None
            
        return DTOMapper.map_candidates(response.get("candidates", []))
