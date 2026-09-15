from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class BaseVectorStore(ABC):
    @abstractmethod
    def add_vectors(self, vectors: List[List[float]], payloads: List[Dict[str, Any]], ids: List[str]) -> bool:
        """Stores vectors along with chunk payload and metadata filters."""
        pass

    @abstractmethod
    def search_similar(
        self,
        query_vector: List[float],
        limit: int = 5,
        allowed_roles: Optional[List[str]] = None,
        user_id: Optional[str] = None,
        knowledge_base_ids: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Performs vector similarity search constrained strictly by metadata access filters."""
        pass

    @abstractmethod
    def delete_by_document_id(self, document_id: str) -> bool:
        """Removes all vector embeddings associated with a deleted document."""
        pass
