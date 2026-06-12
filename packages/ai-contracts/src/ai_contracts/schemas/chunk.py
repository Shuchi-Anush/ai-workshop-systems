from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from ai_contracts.schemas.common import BaseMetadata

class ChunkMetadata(BaseMetadata):
    model_config = ConfigDict(extra="allow")
    
    document_id: str
    chunk_id: str
    source_file: str
    chunk_strategy: str
    parser_version: str
    parent_chunk_id: Optional[str] = None

class DocumentChunk(BaseModel):
    model_config = ConfigDict(extra="allow")
    
    metadata: ChunkMetadata
    content: str
    token_count: int
