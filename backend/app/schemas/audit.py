from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AuditLogResponse(BaseModel):
    id: str
    user_id: str
    user_email: str
    user_role: str
    query_text: str
    knowledge_base_ids: Optional[str] = None
    retrieved_chunk_ids: Optional[str] = None
    response_summary: Optional[str] = None
    response_latency_ms: float
    is_flagged_prompt_injection: bool
    timestamp: datetime

    class Config:
        from_attributes = True

class SystemHealthResponse(BaseModel):
    status: str
    database: str
    vector_store: str
    llm_provider: str
    embedding_provider: str
    version: str
