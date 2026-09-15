from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.rag import RAGQueryRequest, RAGQueryResponse
from app.models.user import User
from app.services.auth_service import get_current_user
from app.services.rag_service import RAGService
from app.services.audit_service import AuditService

router = APIRouter(prefix="/rag", tags=["RAG Conversational Engine"])
rag_service = RAGService()

@router.post("/query", response_model=RAGQueryResponse)
def execute_rag_query(
    request: RAGQueryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not request.query or not request.query.strip():
        raise HTTPException(status_code=400, detail="Query string cannot be empty.")

    # Execute RAG pipeline
    response = rag_service.query(request, current_user)

    # Log to audit trial
    chunk_ids = [c.document_id for c in response.citations]
    AuditService.log_query(
        db=db,
        user=current_user,
        query_text=request.query,
        knowledge_base_ids=request.knowledge_base_ids,
        retrieved_chunk_ids=chunk_ids,
        response_summary=response.answer,
        latency_ms=response.execution_time_ms,
        is_injection=response.is_flagged_prompt_injection
    )

    return response

@router.post("/stream")
def execute_rag_stream(
    request: RAGQueryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    response = rag_service.query(request, current_user)
    
    def event_stream():
        # Yield metadata event
        yield f"data: {{\"retrieved_chunks\": {response.retrieved_chunk_count}, \"latency_ms\": {response.execution_time_ms}}}\n\n"
        # Stream text response
        words = response.answer.split(" ")
        for w in words:
            yield f"data: {w} \n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
