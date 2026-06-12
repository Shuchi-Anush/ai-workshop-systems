from abc import ABC, abstractmethod
from shared.schemas.domain import ResumeDocument

class ICleaner(ABC):
    """
    Abstract base class for text normalization and artifact removal.
    """
    
    @abstractmethod
    def clean(self, document: ResumeDocument) -> ResumeDocument:
        pass
