import numpy as np
from typing import List, Dict, Any, Optional
from ai_contracts.interfaces.vectordb import IVectorDB
from ai_vector.schemas.vector import VectorRecord, VectorSearchResult, EmbeddingVector

class MockVectorDB(IVectorDB):
    """
    Deterministic in-memory vector database using NumPy cosine similarity.
    Designed for architecture stabilization and offline testing.
    """
    
    def __init__(self):
        self._records: Dict[str, VectorRecord] = {}
        
    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        # Avoid division by zero
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(np.dot(a, b) / (norm_a * norm_b))
        
    def upsert(self, records: List[VectorRecord]) -> None:
        for record in records:
            self._records[record.chunk_id] = record
            
    def search(self, query_vector: EmbeddingVector, top_k: int, filters: Optional[Dict[str, Any]] = None) -> List[VectorSearchResult]:
        q_vec = np.array(query_vector.vector)
        
        results = []
        for chunk_id, record in self._records.items():
            r_vec = np.array(record.embedding.vector)
            sim = self._cosine_similarity(q_vec, r_vec)
            results.append(
                VectorSearchResult(
                    chunk_id=chunk_id,
                    similarity_score=sim,
                    distance=1.0 - sim  # Simple distance mapping
                )
            )
            
        # Sort descending by similarity, then alphabetically by chunk_id for determinism
        results.sort(key=lambda x: (-x.similarity_score, x.chunk_id))
        
        return results[:top_k]
        
    def delete(self, chunk_ids: List[str]) -> None:
        for cid in chunk_ids:
            self._records.pop(cid, None)
            
    def clear(self) -> None:
        """Helper for tests to reset state."""
        self._records.clear()
