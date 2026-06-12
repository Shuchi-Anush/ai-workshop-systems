from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from .domain import DocumentChunk
from .common import TimestampMixin

class RetrievalQuery(BaseModel):
    query_text: str
    top_k: int = 10
    filters: Optional[Dict[str, Any]] = None
    trace_id: Optional[str] = None

class RetrievedChunk(BaseModel):
    chunk: DocumentChunk
    similarity_score: float

class RetrievalResult(TimestampMixin):
    query: RetrievalQuery
    results: List[RetrievedChunk]
    execution_time_ms: float
