from typing import Dict, Any, List
from apps.resume_analyzer.frontend.models.domain import CandidateCard, CandidateProfile, MatchTier
from apps.resume_analyzer.frontend.utils.score_mapper import map_raw_score_to_percentage, get_match_tier

class DTOMapper:
    """Converts raw backend JSON into typed frontend models (Recruiter abstractions)."""
    
    @staticmethod
    def map_candidate(raw: Dict[str, Any]) -> CandidateCard:
        cand_dict = raw.get("candidate", {})
        diag_dict = raw.get("diagnostics", {})
        explain_dict = diag_dict.get("explainability", {})
        
        # Safe extraction of basic info
        cid = cand_dict.get("candidate_id", "Unknown Candidate")
        name = cand_dict.get("name", cid.replace("_", " ").title())
        skills = cand_dict.get("skills", [])
        experience = cand_dict.get("experience", "Experience details unavailable")
        education = cand_dict.get("education", "Education details unavailable")
        
        profile = CandidateProfile(
            id=cid,
            name=name,
            skills=skills,
            experience=experience,
            education=education
        )
        
        # Calculate recruiter-friendly score
        raw_score = raw.get("score", 0.0)
        match_percent = map_raw_score_to_percentage(raw_score)
        tier_str = get_match_tier(match_percent)
        match_tier = MatchTier(tier_str)
        
        # Extract recruiter insights (Strengths, missing, flags)
        # Assuming the backend provides matched sparse terms as strengths for now
        strengths = explain_dict.get("matched_sparse_terms", [])
        missing_skills = [] # Future: backend could provide this
        
        flags = []
        penalty = explain_dict.get("adversarial_penalty", 1.0)
        if penalty < 1.0:
            flags.append("⚠️ Irregular Formatting Detected")
        
        # Keep raw data for Technical Insights
        return CandidateCard(
            candidate=profile,
            match_score_percent=match_percent,
            match_tier=match_tier,
            strengths=strengths,
            missing_skills=missing_skills,
            flags=flags,
            raw_data=raw
        )
        
    @staticmethod
    def map_candidates(raw_list: List[Dict[str, Any]]) -> List[CandidateCard]:
        return [DTOMapper.map_candidate(c) for c in raw_list]
