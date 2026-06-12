from abc import ABC, abstractmethod
from typing import List, Optional, TypeVar, Generic

CandidateT = TypeVar("CandidateT")
ChunkT = TypeVar("ChunkT")

class IMetadataStore(ABC, Generic[CandidateT, ChunkT]):
    """
    Relational metadata storage interface (e.g., PostgreSQL).
    Isolates business entity persistence from vector storage.
    """
    
    @abstractmethod
    def save_candidate(self, candidate: CandidateT) -> None:
        pass
        
    @abstractmethod
    def get_candidate(self, candidate_id: str) -> Optional[CandidateT]:
        pass
        
    @abstractmethod
    def save_chunks(self, chunks: List[ChunkT]) -> None:
        pass
        
    @abstractmethod
    def get_chunks_by_ids(self, chunk_ids: List[str]) -> List[ChunkT]:
        pass
        
    @abstractmethod
    def get_chunks_by_candidate(self, candidate_id: str) -> List[ChunkT]:
        pass
