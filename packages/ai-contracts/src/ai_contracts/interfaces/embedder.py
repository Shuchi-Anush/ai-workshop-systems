from abc import ABC, abstractmethod
from typing import List, Union
from shared.schemas.domain import DocumentChunk
from shared.schemas.vector import EmbeddingVector

class IEmbedder(ABC):
    """
    Converts text or DocumentChunks into dense vector representations.
    """
    
    @abstractmethod
    def embed_text(self, text: str) -> EmbeddingVector:
        pass
        
    @abstractmethod
    def embed_chunks(self, chunks: List[DocumentChunk]) -> List[EmbeddingVector]:
        pass
        
    @abstractmethod
    async def embed_chunks_async(self, chunks: List[DocumentChunk]) -> List[EmbeddingVector]:
        pass
