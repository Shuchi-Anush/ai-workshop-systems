from abc import ABC, abstractmethod
from typing import List, TypeVar, Generic
from ai_contracts.schemas.chunk import DocumentChunk

EmbeddingVectorT = TypeVar("EmbeddingVectorT")

class IEmbedder(ABC, Generic[EmbeddingVectorT]):
    """
    Converts text or DocumentChunks into dense vector representations.
    """
    
    @abstractmethod
    def embed_text(self, text: str) -> EmbeddingVectorT:
        pass
        
    @abstractmethod
    def embed_chunks(self, chunks: List[DocumentChunk]) -> List[EmbeddingVectorT]:
        pass
        
    @abstractmethod
    async def embed_chunks_async(self, chunks: List[DocumentChunk]) -> List[EmbeddingVectorT]:
        pass
