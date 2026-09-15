from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class KnowledgeBaseCreate(BaseModel):
    name: str
    description: Optional[str] = None
    access_level: str = "Public"

class KnowledgeBaseResponse(KnowledgeBaseCreate):
    id: str
    owner_id: str
    created_at: datetime
    document_count: int = 0

    class Config:
        from_attributes = True

class DocumentResponse(BaseModel):
    id: str
    title: str
    file_name: str
    file_type: str
    file_size: int
    knowledge_base_id: str
    owner_id: str
    status: str
    error_message: Optional[str] = None
    is_public: bool
    allowed_roles: str
    chunk_count: int
    created_at: datetime

    class Config:
        from_attributes = True

class DocumentPermissionsUpdate(BaseModel):
    is_public: bool
    allowed_roles: List[str]
