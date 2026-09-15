import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Float, Text
from app.core.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False)
    user_email = Column(String, nullable=False)
    user_role = Column(String, nullable=False)
    query_text = Column(Text, nullable=False)
    knowledge_base_ids = Column(String, nullable=True)
    retrieved_chunk_ids = Column(Text, nullable=True)
    response_summary = Column(Text, nullable=True)
    response_latency_ms = Column(Float, default=0.0)
    is_flagged_prompt_injection = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
