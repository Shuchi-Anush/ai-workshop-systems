from abc import ABC, abstractmethod
from typing import List
from shared.schemas.retrieval import RetrievedChunk
from shared.schemas.ranking import RankedCandidate, RankingResult

class ICandidateAggregator(ABC):
    """
    Groups retrieved chunks by candidate to form the basis for candidate-level scoring.
    """
    
    @abstractmethod
    def aggregate(self, retrieved_chunks: List[RetrievedChunk]) -> List[RankedCandidate]:
        pass

class IRanker(ABC):
    """
    Scores and sorts aggregated candidates based on heuristics and vector similarity.
    """
    
    @abstractmethod
    def rank(self, candidates: List[RankedCandidate], job_description: str) -> RankingResult:
        pass
