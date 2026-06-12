import os
from pathlib import Path

base_dir = Path("d:/ai-workshop-systems/shared")
mocks_dir = base_dir / "mocks"
providers_dir = base_dir / "providers"

mocks_dir.mkdir(parents=True, exist_ok=True)
providers_dir.mkdir(parents=True, exist_ok=True)

files_content = {
    "mocks/__init__.py": "",
    "mocks/mock_vectordb.py": """import numpy as np
from typing import List, Dict, Any, Optional
from shared.interfaces.vectordb import IVectorDB
from shared.schemas.vector import VectorRecord, VectorSearchResult, EmbeddingVector

class MockVectorDB(IVectorDB):
    \"\"\"
    Deterministic in-memory vector database using NumPy cosine similarity.
    Designed for architecture stabilization and offline testing.
    \"\"\"
    
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
        \"\"\"Helper for tests to reset state.\"\"\"
        self._records.clear()
""",

    "mocks/mock_metadata_store.py": """from typing import List, Optional, Dict
from shared.interfaces.storage import IMetadataStore
from shared.schemas.domain import Candidate, DocumentChunk

class MockMetadataStore(IMetadataStore):
    \"\"\"
    In-memory relational store mock. 
    Simulates PostgreSQL behavior for metadata isolation.
    \"\"\"
    
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
        \"\"\"Helper for tests to reset state.\"\"\"
        self._candidates.clear()
        self._chunks.clear()
""",

    "providers/__init__.py": "",
    "providers/registry.py": """from typing import Dict, Type, Any, Callable
from shared.interfaces.vectordb import IVectorDB
from shared.interfaces.storage import IMetadataStore

class DependencyRegistry:
    \"\"\"
    Lightweight dependency registry.
    Prevents hardcoded implementation imports in the service layer.
    \"\"\"
    
    def __init__(self):
        self._services: Dict[Type, Any] = {}
        self._factories: Dict[Type, Callable[[], Any]] = {}
        
    def register_singleton(self, interface: Type, implementation: Any) -> None:
        self._services[interface] = implementation
        
    def register_factory(self, interface: Type, factory: Callable[[], Any]) -> None:
        self._factories[interface] = factory
        
    def resolve(self, interface: Type) -> Any:
        if interface in self._services:
            return self._services[interface]
        if interface in self._factories:
            return self._factories[interface]()
            
        raise ValueError(f"No registered implementation found for {interface.__name__}")
        
    def clear(self) -> None:
        self._services.clear()
        self._factories.clear()
""",

    "providers/container.py": """from .registry import DependencyRegistry

# Global container instance for the application lifecycle.
# In a full FastAPI app, this might be attached to app.state.
global_container = DependencyRegistry()

def get_container() -> DependencyRegistry:
    return global_container
""",

    "providers/factories.py": """from shared.interfaces.vectordb import IVectorDB
from shared.interfaces.storage import IMetadataStore
from shared.mocks.mock_vectordb import MockVectorDB
from shared.mocks.mock_metadata_store import MockMetadataStore
from .container import get_container

def configure_mock_infrastructure() -> None:
    \"\"\"
    Wires the container with mock implementations.
    To be used during test initialization and offline architecture stabilization.
    \"\"\"
    container = get_container()
    
    # Register singletons to preserve state across service calls during testing
    container.register_singleton(IVectorDB, MockVectorDB())
    container.register_singleton(IMetadataStore, MockMetadataStore())
"""
}

for path_str, content in files_content.items():
    full_path = base_dir / path_str
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

print(f"Successfully generated {len(files_content)} mock and provider files.")
