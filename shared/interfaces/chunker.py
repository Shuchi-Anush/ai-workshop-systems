from abc import ABC, abstractmethod
from typing import List
from shared.schemas.domain import ResumeDocument, DocumentChunk

class ISectionParser(ABC):
    """
    Identifies and tags semantic sections within a cleaned document.
    """
    
    @abstractmethod
    def parse_sections(self, document: ResumeDocument) -> ResumeDocument:
        pass

class IChunker(ABC):
    """
    Divides semantic sections into embeddable DocumentChunks.
    """
    
    @abstractmethod
    def chunk(self, document: ResumeDocument) -> List[DocumentChunk]:
        pass
