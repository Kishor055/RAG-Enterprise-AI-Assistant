import os
import math
from typing import List, Dict, Any, Optional
from app.interfaces.vector_store import BaseVectorStore
from app.core.config import settings

class ChromaVectorStore(BaseVectorStore):
    _shared_memory_store: List[Dict[str, Any]] = []

    def __init__(self, persist_dir: str = settings.CHROMA_PERSIST_DIRECTORY):

        self.persist_dir = persist_dir
        self.chroma_client = None
        self.collection = None
        self._memory_store = ChromaVectorStore._shared_memory_store


        try:
            import chromadb
            self.chroma_client = chromadb.PersistentClient(path=self.persist_dir)
            self.collection = self.chroma_client.get_or_create_collection(
                name="rag_enterprise_chunks",
                metadata={"hnsw:space": "cosine"}
            )
        except Exception:
            self.chroma_client = None
            self.collection = None

    def add_vectors(self, vectors: List[List[float]], payloads: List[Dict[str, Any]], ids: List[str]) -> bool:
        if self.collection:
            metadatas = []
            for payload in payloads:
                # Sanitize metadata values for Chroma compatibility (primitives or lists of primitives)
                cleaned = {}
                for k, v in payload.items():
                    if isinstance(v, (str, int, float, bool)):
                        cleaned[k] = v
                    elif isinstance(v, list):
                        cleaned[k] = ",".join(str(item) for item in v)
                    else:
                        cleaned[k] = str(v)
                metadatas.append(cleaned)
            
            documents = [p.get("text", "") for p in payloads]
            self.collection.add(
                ids=ids,
                embeddings=vectors,
                metadatas=metadatas,
                documents=documents
            )
            return True
        else:
            # Memory store fallback
            for i, vector_id in enumerate(ids):
                self._memory_store.append({
                    "id": vector_id,
                    "vector": vectors[i],
                    "payload": payloads[i]
                })
            return True

    def search_similar(
        self,
        query_vector: List[float],
        limit: int = 5,
        allowed_roles: Optional[List[str]] = None,
        user_id: Optional[str] = None,
        knowledge_base_ids: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        allowed_roles = allowed_roles or ["Standard User"]
        results = []

        if self.collection:
            try:
                # Query Chroma
                res = self.collection.query(
                    query_embeddings=[query_vector],
                    n_results=min(limit * 4, 100)  # Overfetch to filter security bounds
                )
                
                if res and res.get("ids") and res["ids"][0]:
                    ids = res["ids"][0]
                    metadatas = res["metadatas"][0] if res.get("metadatas") else []
                    documents = res["documents"][0] if res.get("documents") else []
                    distances = res["distances"][0] if res.get("distances") else []

                    for i in range(len(ids)):
                        meta = metadatas[i] if i < len(metadatas) else {}
                        doc_text = documents[i] if i < len(documents) else ""
                        dist = distances[i] if i < len(distances) else 1.0
                        score = max(0.0, 1.0 - float(dist))

                        # Document-Level Security (DLS) Filtering
                        kb_id = meta.get("knowledge_base_id", "")
                        if knowledge_base_ids and kb_id not in knowledge_base_ids:
                            continue

                        is_public = str(meta.get("is_public", "true")).lower() == "true"
                        owner_id = meta.get("owner_id", "")
                        chunk_roles = meta.get("allowed_roles", "").split(",")

                        has_access = (
                            is_public or 
                            "Admin" in allowed_roles or 
                            owner_id == user_id or 
                            any(r in allowed_roles for r in chunk_roles if r)
                        )

                        if not has_access:
                            continue

                        results.append({
                            "chunk_id": ids[i],
                            "document_id": meta.get("document_id", ""),
                            "document_title": meta.get("document_title", "Document"),
                            "file_name": meta.get("file_name", ""),
                            "page_number": int(meta.get("page_number", 1)),
                            "text": doc_text or meta.get("text", ""),
                            "similarity_score": round(score, 4),
                            "metadata": meta
                        })
                        if len(results) >= limit:
                            break
                return results
            except Exception:
                pass

        # In-memory vector cosine similarity search fallback
        scored = []
        for item in self._memory_store:
            payload = item["payload"]
            kb_id = payload.get("knowledge_base_id", "")
            if knowledge_base_ids and kb_id not in knowledge_base_ids:
                continue

            is_public = payload.get("is_public", True)
            owner_id = payload.get("owner_id", "")
            chunk_roles = payload.get("allowed_roles", "Admin,Knowledge Manager,Standard User")
            if isinstance(chunk_roles, str):
                chunk_roles = chunk_roles.split(",")

            has_access = (
                is_public or 
                "Admin" in allowed_roles or 
                owner_id == user_id or 
                any(r in allowed_roles for r in chunk_roles if r)
            )

            if not has_access:
                continue

            # Compute Cosine Similarity
            dot = sum(a * b for a, b in zip(query_vector, item["vector"]))
            norm_a = math.sqrt(sum(a * a for a in query_vector))
            norm_b = math.sqrt(sum(b * b for b in item["vector"]))
            sim = dot / (norm_a * norm_b) if norm_a > 0 and norm_b > 0 else 0.0

            scored.append((sim, item))

        scored.sort(key=lambda x: x[0], reverse=True)
        for sim, item in scored[:limit]:
            payload = item["payload"]
            results.append({
                "chunk_id": item["id"],
                "document_id": payload.get("document_id", ""),
                "document_title": payload.get("document_title", "Document"),
                "file_name": payload.get("file_name", ""),
                "page_number": payload.get("page_number", 1),
                "text": payload.get("text", ""),
                "similarity_score": round(float(sim), 4),
                "metadata": payload
            })

        return results

    def delete_by_document_id(self, document_id: str) -> bool:
        if self.collection:
            try:
                self.collection.delete(where={"document_id": document_id})
            except Exception:
                pass
        
        self._memory_store = [
            item for item in self._memory_store 
            if item["payload"].get("document_id") != document_id
        ]
        return True
