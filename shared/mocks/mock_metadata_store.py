from typing import List, Optional, Dict
from shared.interfaces.storage import IMetadataStore
from shared.schemas.domain import Candidate, DocumentChunk

class MockMetadataStore(IMetadataStore):
    """
    In-memory relational store mock. 
    Simulates PostgreSQL behavior for metadata isolation.
    """
    
    def __init__(self):
        self._candidates: Dict[str, Candidate] = {}
        self._chunks: Dict[str, DocumentChunk] = {}
        
    def save_candidate(self, candidate: Candidate) -> None:
        self._candidates[candidate.candidate_id] = candidate
        
    def get_candidate(self, candidate_id: str) -> Optional[Candidate]:
        return self._candidates.get(candidate_id)
        
    def save_chunks(self, chunks: List[DocumentChunk]) -> None:
        for chunk in chunks:
            self._chunks[chunk.metadata.chunk_id] = chunk
            
    def get_chunks_by_ids(self, chunk_ids: List[str]) -> List[DocumentChunk]:
        # Return only chunks that exist, mimicking DB lookup
        results = [self._chunks[cid] for cid in chunk_ids if cid in self._chunks]
        # Ensure deterministic return order matching the input query order
        return results
        
    def get_chunks_by_candidate(self, candidate_id: str) -> List[DocumentChunk]:
        results = [
            chunk for chunk in self._chunks.values() 
            if chunk.metadata.candidate_id == candidate_id
        ]
        # Deterministic sorting by chunk_id
        results.sort(key=lambda x: x.metadata.chunk_id)
        return results
        
    def clear(self) -> None:
        """Helper for tests to reset state."""
        self._candidates.clear()
        self._chunks.clear()
