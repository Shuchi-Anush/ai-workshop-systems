from abc import ABC, abstractmethod
from typing import List, TypeVar, Generic
from ai_contracts.schemas.chunk import DocumentChunk

DocT = TypeVar("DocT")

class ISectionParser(ABC, Generic[DocT]):
    """
    Identifies and tags semantic sections within a cleaned document.
    """
    
    @abstractmethod
    def parse_sections(self, document: DocT) -> DocT:
        pass

class IChunker(ABC, Generic[DocT]):
    """
    Divides semantic sections into embeddable DocumentChunks.
    """
    
    @abstractmethod
    def chunk(self, document: DocT) -> List[DocumentChunk]:
        pass
