from abc import ABC, abstractmethod
from typing import BinaryIO, TypeVar, Generic
from ai_contracts.schemas.ingestion import ParsingResult

DocT = TypeVar("DocT")

class IParser(ABC, Generic[DocT]):
    """
    Abstract base class for document parsing.
    Responsible for extracting raw text from bytes.
    """
    
    @abstractmethod
    def parse(self, file_stream: BinaryIO, file_name: str) -> ParsingResult[DocT]:
        pass
        
    @abstractmethod
    async def parse_async(self, file_stream: BinaryIO, file_name: str) -> ParsingResult[DocT]:
        pass
