import re
from typing import List, Dict, Any
from abc import ABC, abstractmethod

class BaseFetcher(ABC):
    def __init__(self, keywords: Dict[str, List[str]]):
        self.keywords = keywords

    def get_matches(self, text: str) -> List[str]:
        found_matches = []
        text_lower = text.lower()
        for category, kws in self.keywords.items():
            for kw in kws:
                kw_lower = kw.lower()
                pattern = r'\b' + re.escape(kw_lower) + r'\b'
                if re.search(pattern, text_lower):
                    found_matches.append(kw)
        return list(set(found_matches))

    @abstractmethod
    def fetch(self) -> List[Dict[str, Any]]:
        pass
