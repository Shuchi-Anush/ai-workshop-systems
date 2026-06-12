from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from shared.schemas.vector import VectorRecord, VectorSearchResult, EmbeddingVector

class IVectorDB(ABC):
    """
    Interface for vector storage and similarity search.
    Must NOT leak implementation details (e.g., FAISS indices) to callers.
    """
    
    @abstractmethod
    def upsert(self, records: List[VectorRecord]) -> None:
        pass
        
    @abstractmethod
    def search(self, query_vector: EmbeddingVector, top_k: int, filters: Optional[Dict[str, Any]] = None) -> List[VectorSearchResult]:
        pass
        
    @abstractmethod
    def delete(self, chunk_ids: List[str]) -> None:
        pass
