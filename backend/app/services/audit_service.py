from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.audit import AuditLog
from app.models.user import User

class AuditService:
    @staticmethod
    def log_query(
        db: Session,
        user: User,
        query_text: str,
        knowledge_base_ids: Optional[List[str]],
        retrieved_chunk_ids: List[str],
        response_summary: str,
        latency_ms: float,
        is_injection: bool = False
    ) -> AuditLog:
        log_entry = AuditLog(
            user_id=user.id,
            user_email=user.email,
            user_role=user.role,
            query_text=query_text,
            knowledge_base_ids=",".join(knowledge_base_ids) if knowledge_base_ids else "All",
            retrieved_chunk_ids=",".join(retrieved_chunk_ids),
            response_summary=response_summary[:300],
            response_latency_ms=latency_ms,
            is_flagged_prompt_injection=is_injection
        )
        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)
        return log_entry

    @staticmethod
    def get_audit_logs(db: Session, limit: int = 50, skip: int = 0) -> List[AuditLog]:
        return db.query(AuditLog).order_by(AuditLog.timestamp.desc()).offset(skip).limit(limit).all()
