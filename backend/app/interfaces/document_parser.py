from abc import ABC, abstractmethod
from typing import List, Dict, Any

class ParsedPage(ABC):
    def __init__(self, page_number: int, text: str):
        self.page_number = page_number
        self.text = text

class BaseDocumentParser(ABC):
    @abstractmethod
    def parse_file(self, file_path: str) -> List[ParsedPage]:
        """Parses a document file and returns structured text by page or section."""
        pass
