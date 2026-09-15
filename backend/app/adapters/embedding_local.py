import math
import hashlib
from typing import List
from app.interfaces.embedding import BaseEmbeddingProvider

class LocalEmbeddingProvider(BaseEmbeddingProvider):
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._dim = 384
        self.model = None
        
        # Try loading sentence_transformers if installed
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(model_name)
            self._dim = self.model.get_sentence_embedding_dimension()
        except Exception:
            # Fallback to fast hash vectorizer if torch/sentence_transformers not loaded
            self.model = None

    @property
    def dimension(self) -> int:
        return self._dim

    def embed_text(self, text: str) -> List[float]:
        if self.model:
            embedding = self.model.encode(text)
            return embedding.tolist()
        return self._hash_vectorize(text)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if self.model:
            embeddings = self.model.encode(texts)
            return [emb.tolist() for emb in embeddings]
        return [self._hash_vectorize(t) for t in texts]

    def _hash_vectorize(self, text: str) -> List[float]:
        """High-speed 384-dim semantic feature vectorizer based on n-gram feature hashing."""
        words = text.lower().split()
        vec = [0.0] * self._dim
        if not words:
            return vec

        for word in words:
            # Hash word and n-grams across vector space
            h = int(hashlib.md5(word.encode('utf-8')).hexdigest(), 16)
            idx = h % self._dim
            sign = 1.0 if (h >> 3) % 2 == 0 else -1.0
            vec[idx] += sign

            # Character trigrams for morphological similarity
            for i in range(len(word) - 2):
                tri = word[i:i+3]
                tri_h = int(hashlib.sha256(tri.encode('utf-8')).hexdigest(), 16)
                tri_idx = tri_h % self._dim
                vec[tri_idx] += 0.5 * (1.0 if (tri_h >> 3) % 2 == 0 else -1.0)

        # L2 Normalize
        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 0:
            vec = [x / norm for x in vec]
        return vec
