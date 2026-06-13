from abc import ABC, abstractmethod
from typing import List

class ISkillExtractor(ABC):
    @abstractmethod
    def extract(self, text: str) -> List[str]:
        """Extracts a normalized boolean array of hard technical skills."""
        pass
