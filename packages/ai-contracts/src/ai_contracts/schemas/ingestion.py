from typing import Optional, List, Generic, TypeVar
from pydantic import BaseModel
from ai_contracts.schemas.common import ProcessingStatus, ErrorInfo
from ai_contracts.schemas.chunk import DocumentChunk

DocT = TypeVar("DocT")

class ParsingResult(BaseModel, Generic[DocT]):
    status: ProcessingStatus
    document: Optional[DocT] = None
    error: Optional[ErrorInfo] = None

class ChunkingResult(BaseModel):
    status: ProcessingStatus
    chunks: List[DocumentChunk] = []
    error: Optional[ErrorInfo] = None
