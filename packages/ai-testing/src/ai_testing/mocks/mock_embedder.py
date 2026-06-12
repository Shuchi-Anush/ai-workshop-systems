import hashlib
import numpy as np
from typing import List
from ai_contracts.interfaces.embedder import IEmbedder
from shared.schemas.domain import DocumentChunk
from ai_vector.schemas.vector import EmbeddingVector

class MockEmbedder(IEmbedder):
    """
    Deterministic mock embedder.
    Uses MD5 hashing to generate consistent pseudorandom vectors from text.
    Designed purely for orchestration validation and reproducible tests.
    """
    
    def __init__(self, dimensions: int = 384):
        self.dimensions = dimensions
        self.model_name = "mock-hashing-embedder"
        self.model_version = "v1.0.0"
        
    def _text_to_deterministic_vector(self, text: str) -> np.ndarray:
        # Generate a deterministic seed from the text
        seed_bytes = hashlib.md5(text.encode('utf-8')).digest()
        seed = int.from_bytes(seed_bytes[:4], byteorder='little')
        
        # Use the seed to generate a reproducible "random" vector
        rng = np.random.RandomState(seed)
        vec = rng.uniform(-1.0, 1.0, self.dimensions)
        
        # Normalize the vector for cosine similarity
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
            
        return vec

    def embed_text(self, text: str) -> EmbeddingVector:
        vec = self._text_to_deterministic_vector(text)
        return EmbeddingVector(
            vector=vec.tolist(),
            dimensions=self.dimensions,
            model_name=self.model_name,
            model_version=self.model_version
        )
        
    def embed_chunks(self, chunks: List[DocumentChunk]) -> List[EmbeddingVector]:
        return [self.embed_text(chunk.content) for chunk in chunks]
        
    async def embed_chunks_async(self, chunks: List[DocumentChunk]) -> List[EmbeddingVector]:
        # Sync execution wrapper for mock async behavior
        return self.embed_chunks(chunks)
