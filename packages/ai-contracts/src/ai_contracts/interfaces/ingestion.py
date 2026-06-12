from abc import ABC, abstractmethod
from shared.schemas.ingestion import IngestionRequest, IngestionResult

class IIngestionService(ABC):
    """
    Orchestrates the entire ingestion lifecycle.
    """
    
    @abstractmethod
    def ingest(self, request: IngestionRequest) -> IngestionResult:
        pass
        
    @abstractmethod
    async def ingest_async(self, request: IngestionRequest) -> IngestionResult:
        pass
