from typing import List, Dict, Optional
from pydantic import BaseModel
from .domain import Candidate
from .retrieval import RetrievedChunk
from .common import TimestampMixin

class RankingBreakdown(BaseModel):
    base_similarity_score: float
    skill_overlap_bonus: float = 0.0
    experience_bonus: float = 0.0
    section_weight_bonus: float = 0.0

class CandidateScore(BaseModel):
    final_score: float
    breakdown: RankingBreakdown
    explainability_log: List[str]

class RankedCandidate(BaseModel):
    candidate: Candidate
    score: CandidateScore
    supporting_chunks: List[RetrievedChunk]

class RankingResult(TimestampMixin):
    job_description: str
    ranked_candidates: List[RankedCandidate]
    execution_time_ms: float
