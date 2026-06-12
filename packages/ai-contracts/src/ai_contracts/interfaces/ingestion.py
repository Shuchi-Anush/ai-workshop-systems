from abc import ABC, abstractmethod
from typing import TypeVar, Generic

IngestionRequestT = TypeVar("IngestionRequestT")
IngestionResultT = TypeVar("IngestionResultT")

class IIngestionService(ABC, Generic[IngestionRequestT, IngestionResultT]):
    """
    Orchestrates the entire ingestion lifecycle.
    """
    
    @abstractmethod
    def ingest(self, request: IngestionRequestT) -> IngestionResultT:
        pass
        
    @abstractmethod
    async def ingest_async(self, request: IngestionRequestT) -> IngestionResultT:
        pass
