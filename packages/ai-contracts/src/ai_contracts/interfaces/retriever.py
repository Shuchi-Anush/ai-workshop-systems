from abc import ABC, abstractmethod
from ai_contracts.schemas.retrieval import RetrievalQuery, RetrievalResult

class IRetriever(ABC):
    """
    Coordinates vector search and metadata rehydration.
    """
    
    @abstractmethod
    def retrieve(self, query: RetrievalQuery) -> RetrievalResult:
        pass
        
    @abstractmethod
    async def retrieve_async(self, query: RetrievalQuery) -> RetrievalResult:
        pass
