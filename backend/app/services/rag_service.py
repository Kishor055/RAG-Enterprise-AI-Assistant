import time
import re
from typing import List, Optional, Dict, Any
from app.models.user import User
from app.adapters.embedding_local import LocalEmbeddingProvider
from app.adapters.vector_chroma import ChromaVectorStore
from app.adapters.llm_gemini import GeminiLLMProvider
from app.schemas.rag import RAGQueryRequest, RAGQueryResponse, SourceCitation

class RAGService:
    def __init__(
        self,
        embedding_provider: LocalEmbeddingProvider = None,
        vector_store: ChromaVectorStore = None,
        llm_provider: GeminiLLMProvider = None
    ):
        self.embedder = embedding_provider or LocalEmbeddingProvider()
        self.vector_store = vector_store or ChromaVectorStore()
        self.llm = llm_provider or GeminiLLMProvider()

    def detect_prompt_injection(self, query: str) -> bool:
        """Detect prompt injection patterns targeting LLM override or data exfiltration."""
        patterns = [
            r"ignore (all )?previous instructions",
            r"system prompt",
            r"reveal (all )?secrets",
            r"print (your )?initial instructions",
            r"override safety",
            r"bypass security"
        ]
        lowered = query.lower()
        for p in patterns:
            if re.search(p, lowered):
                return True
        return False

    def query(self, request: RAGQueryRequest, current_user: User) -> RAGQueryResponse:
        start_time = time.time()

        # 1. Prompt Injection Defense
        is_injection = self.detect_prompt_injection(request.query)
        if is_injection:
            return RAGQueryResponse(
                query=request.query,
                answer="⚠️ Security Warning: Your query triggered our prompt injection safety filter. Please rephrase your question using standard natural language business domain terms.",
                citations=[],
                retrieved_chunk_count=0,
                execution_time_ms=round((time.time() - start_time) * 1000, 2),
                is_flagged_prompt_injection=True
            )

        # 2. Embed Query Vector
        query_vector = self.embedder.embed_text(request.query)

        # 3. Secure Vector Search with RBAC Document-Level Access Control (DLS)
        user_roles = [current_user.role]
        if current_user.role == "Admin":
            user_roles.append("Knowledge Manager")

        retrieved = self.vector_store.search_similar(
            query_vector=query_vector,
            limit=request.top_k,
            allowed_roles=user_roles,
            user_id=current_user.id,
            knowledge_base_ids=request.knowledge_base_ids
        )

        # 4. Construct Context & Citations
        citations: List[SourceCitation] = []
        context_chunks = []

        for idx, item in enumerate(retrieved):
            cit_id = idx + 1
            doc_title = item.get("document_title", "Document")
            file_name = item.get("file_name", "file.pdf")
            page_num = item.get("page_number", 1)
            text_snippet = item.get("text", "").strip()

            citation = SourceCitation(
                citation_id=cit_id,
                document_id=item.get("document_id", ""),
                document_title=doc_title,
                file_name=file_name,
                page_number=page_num,
                snippet=text_snippet[:250] + "..." if len(text_snippet) > 250 else text_snippet,
                similarity_score=item.get("similarity_score", 0.0)
            )
            citations.append(citation)

            context_chunks.append(
                f"[Source: {doc_title} (File: {file_name}, Page {page_num})]\n{text_snippet}"
            )

        context_str = "\n\n".join(context_chunks)

        # 5. System Prompt & Grounded Generation
        system_prompt = (
            "You are an Enterprise RAG AI Assistant. Your task is to provide accurate, "
            "professional, and grounded answers strictly based on the provided Context below.\n"
            "Rules:\n"
            "1. Ground every statement in the provided context.\n"
            "2. Always reference source documents using inline citations like [Source: Document Name, Page X].\n"
            "3. If the context does not contain enough information, state clearly: 'I could not find sufficient information in the authorized documents to answer this question.'\n"
            "4. Do NOT make up facts or use external knowledge outside the provided context."
        )

        user_prompt = f"CONTEXT:\n{context_str}\n\nQUESTION: {request.query}"

        # 6. LLM Generation
        answer_text = self.llm.generate_response(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=request.temperature
        )

        exec_time = round((time.time() - start_time) * 1000, 2)

        return RAGQueryResponse(
            query=request.query,
            answer=answer_text,
            citations=citations,
            retrieved_chunk_count=len(retrieved),
            execution_time_ms=exec_time,
            is_flagged_prompt_injection=False
        )
