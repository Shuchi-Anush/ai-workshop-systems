from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, TypeVar, Generic

VectorRecordT = TypeVar("VectorRecordT")
VectorSearchResultT = TypeVar("VectorSearchResultT")
EmbeddingVectorT = TypeVar("EmbeddingVectorT")

class IVectorDB(ABC, Generic[VectorRecordT, VectorSearchResultT, EmbeddingVectorT]):
    """
    Interface for vector storage and similarity search.
    Must NOT leak implementation details (e.g., FAISS indices) to callers.
    """
    
    @abstractmethod
    def upsert(self, records: List[VectorRecordT]) -> None:
        pass
        
    @abstractmethod
    def search(self, query_vector: EmbeddingVectorT, top_k: int, filters: Optional[Dict[str, Any]] = None) -> List[VectorSearchResultT]:
        pass
        
    @abstractmethod
    def delete(self, chunk_ids: List[str]) -> None:
        pass
