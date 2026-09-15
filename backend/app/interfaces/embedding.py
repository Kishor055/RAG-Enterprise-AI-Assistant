from abc import ABC, abstractmethod
from typing import List

class BaseEmbeddingProvider(ABC):
    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        """Generates a single vector embedding for a query string."""
        pass

    @abstractmethod
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generates batch vector embeddings for a list of text chunks."""
        pass

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Returns vector dimension."""
        pass
