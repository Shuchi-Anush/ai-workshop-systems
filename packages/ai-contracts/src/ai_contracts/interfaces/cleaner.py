from abc import ABC, abstractmethod
from typing import TypeVar, Generic

DocT = TypeVar("DocT")

class ICleaner(ABC, Generic[DocT]):
    """
    Cleans raw text (e.g. standardizing whitespace, removing garbled characters).
    """
    
    @abstractmethod
    def clean(self, document: DocT) -> DocT:
        pass
