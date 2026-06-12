from typing import Optional, List
from pydantic import BaseModel
from .common import ProcessingStatus, ErrorInfo, TimestampMixin
from .domain import ResumeDocument, DocumentChunk

class IngestionRequest(BaseModel):
    candidate_id: str
    file_path: str
    trace_id: Optional[str] = None

class ParsingResult(BaseModel):
    status: ProcessingStatus
    document: Optional[ResumeDocument] = None
    error: Optional[ErrorInfo] = None

class ChunkingResult(BaseModel):
    status: ProcessingStatus
    chunks: List[DocumentChunk] = []
    error: Optional[ErrorInfo] = None

class IngestionResult(TimestampMixin):
    candidate_id: str
    document_id: str
    status: ProcessingStatus
    chunks_indexed: int = 0
    error: Optional[ErrorInfo] = None
