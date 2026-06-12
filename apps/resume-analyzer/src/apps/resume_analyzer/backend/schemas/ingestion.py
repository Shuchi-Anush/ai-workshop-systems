from typing import Optional
from pydantic import BaseModel
from ai_contracts.schemas.common import ProcessingStatus, ErrorInfo, TimestampMixin

class IngestionRequest(BaseModel):
    candidate_id: str
    file_path: str
    trace_id: Optional[str] = None

class IngestionResult(TimestampMixin):
    candidate_id: str
    document_id: str
    status: ProcessingStatus
    chunks_indexed: int = 0
    error: Optional[ErrorInfo] = None
