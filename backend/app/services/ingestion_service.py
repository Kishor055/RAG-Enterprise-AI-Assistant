import os
import uuid
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.document import Document, Chunk, KnowledgeBase
from app.adapters.parser_pdf_docx import FileParser
from app.adapters.embedding_local import LocalEmbeddingProvider
from app.adapters.vector_chroma import ChromaVectorStore

class IngestionService:
    def __init__(self, embedding_provider: LocalEmbeddingProvider = None, vector_store: ChromaVectorStore = None):
        self.parser = FileParser()
        self.embedder = embedding_provider or LocalEmbeddingProvider()
        self.vector_store = vector_store or ChromaVectorStore()

    def process_document(self, db: Session, document_id: str) -> Document:
        doc = db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            raise ValueError(f"Document {document_id} not found.")

        doc.status = "Processing"
        db.commit()

        try:
            # 1. Parse File into Pages
            parsed_pages = self.parser.parse_file(doc.file_path)
            
            # 2. Chunk text with overlap
            chunks_to_create = []
            chunk_size = 500  # Target characters per chunk
            overlap = 100

            for page in parsed_pages:
                text = page.text
                if not text:
                    continue
                
                start = 0
                while start < len(text):
                    end = start + chunk_size
                    chunk_str = text[start:end].strip()
                    if chunk_str:
                        chunks_to_create.append({
                            "text": chunk_str,
                            "page_number": page.page_number
                        })
                    start += (chunk_size - overlap)

            if not chunks_to_create:
                doc.status = "Failed"
                doc.error_message = "No extractable text content found in document."
                db.commit()
                return doc

            # 3. Generate Vector Embeddings in Batch
            texts = [c["text"] for c in chunks_to_create]
            embeddings = self.embedder.embed_documents(texts)

            # 4. Prepare Payloads and DB records
            vector_ids = []
            payloads = []
            db_chunks = []

            for idx, item in enumerate(chunks_to_create):
                chunk_id = f"chk_{uuid.uuid4().hex[:12]}"
                vector_ids.append(chunk_id)

                payload = {
                    "document_id": doc.id,
                    "knowledge_base_id": doc.knowledge_base_id,
                    "document_title": doc.title,
                    "file_name": doc.file_name,
                    "owner_id": doc.owner_id,
                    "is_public": doc.is_public,
                    "allowed_roles": doc.allowed_roles,
                    "page_number": item["page_number"],
                    "text": item["text"],
                    "chunk_index": idx
                }
                payloads.append(payload)

                db_chunk = Chunk(
                    id=chunk_id,
                    document_id=doc.id,
                    knowledge_base_id=doc.knowledge_base_id,
                    chunk_index=idx,
                    text=item["text"],
                    page_number=item["page_number"],
                    token_count=len(item["text"].split()),
                    vector_id=chunk_id
                )
                db_chunks.append(db_chunk)

            # 5. Store in Vector Store
            self.vector_store.add_vectors(
                vectors=embeddings,
                payloads=payloads,
                ids=vector_ids
            )

            # 6. Store in Database
            db.bulk_save_objects(db_chunks)
            doc.status = "Indexed"
            doc.chunk_count = len(db_chunks)
            doc.error_message = None
            db.commit()
            db.refresh(doc)
            return doc

        except Exception as e:
            doc.status = "Failed"
            doc.error_message = str(e)
            db.commit()
            raise e
