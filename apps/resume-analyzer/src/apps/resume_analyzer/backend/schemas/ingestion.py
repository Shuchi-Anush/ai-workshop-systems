from typing import Optional
from pydantic import BaseModel
from ai_contracts.schemas.common import ProcessingStatus, ErrorInfo, TimestampMixin

from pydantic import ConfigDict
from typing import Any

class IngestionRequest(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    candidate_id: str
    file_stream: Any
    file_name: str
    trace_id: Optional[str] = None

class IngestionResult(TimestampMixin):
    candidate_id: str
    document_id: str
    status: ProcessingStatus
    chunks_indexed: int = 0
    error: Optional[ErrorInfo] = None
