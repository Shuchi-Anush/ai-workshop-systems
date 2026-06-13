from typing import List, Union, Dict, Any, Optional
from pydantic import BaseModel, ConfigDict
import numpy as np

class EmbeddingVector(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    vector: Union[List[float], Any]
    dimensions: int
    model_name: str
    model_version: str

class VectorRecord(BaseModel):
    chunk_id: str
    embedding: EmbeddingVector
    metadata: Dict[str, Any] = {}
    
class VectorSearchResult(BaseModel):
    chunk_id: str
    similarity_score: float
    distance: Optional[float] = None