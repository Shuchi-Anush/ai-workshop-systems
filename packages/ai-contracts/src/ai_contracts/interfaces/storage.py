from abc import ABC, abstractmethod
from typing import List, Optional
from shared.schemas.domain import Candidate, DocumentChunk

class IMetadataStore(ABC):
    """
    Relational metadata storage interface (e.g., PostgreSQL).
    Isolates business entity persistence from vector storage.
    """
    
    @abstractmethod
    def save_candidate(self, candidate: Candidate) -> None:
        pass
        
    @abstractmethod
    def get_candidate(self, candidate_id: str) -> Optional[Candidate]:
        pass
        
    @abstractmethod
    def save_chunks(self, chunks: List[DocumentChunk]) -> None:
        pass
        
    @abstractmethod
    def get_chunks_by_ids(self, chunk_ids: List[str]) -> List[DocumentChunk]:
        pass
        
    @abstractmethod
    def get_chunks_by_candidate(self, candidate_id: str) -> List[DocumentChunk]:
        pass
