from abc import ABC, abstractmethod
from typing import BinaryIO
from shared.schemas.ingestion import ParsingResult

class IParser(ABC):
    """
    Abstract base class for document parsing.
    Responsible for extracting raw text from bytes.
    """
    
    @abstractmethod
    def parse(self, file_stream: BinaryIO, file_name: str) -> ParsingResult:
        pass
        
    @abstractmethod
    async def parse_async(self, file_stream: BinaryIO, file_name: str) -> ParsingResult:
        pass
