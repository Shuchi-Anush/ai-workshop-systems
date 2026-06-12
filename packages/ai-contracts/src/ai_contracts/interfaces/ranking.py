from abc import ABC, abstractmethod
from typing import List, TypeVar, Generic

RetrievedChunkT = TypeVar("RetrievedChunkT")
RankedCandidateT = TypeVar("RankedCandidateT")
RankingResultT = TypeVar("RankingResultT")

class ICandidateAggregator(ABC, Generic[RetrievedChunkT, RankedCandidateT]):
    """
    Groups retrieved chunks by candidate to form the basis for candidate-level scoring.
    """
    
    @abstractmethod
    def aggregate(self, retrieved_chunks: List[RetrievedChunkT]) -> List[RankedCandidateT]:
        pass

class IRanker(ABC, Generic[RankedCandidateT, RankingResultT]):
    """
    Scores and sorts aggregated candidates based on heuristics and vector similarity.
    """
    
    @abstractmethod
    def rank(self, candidates: List[RankedCandidateT], job_description: str) -> RankingResultT:
        pass
