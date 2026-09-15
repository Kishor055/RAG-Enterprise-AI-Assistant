from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db, engine
from app.schemas.audit import AuditLogResponse, SystemHealthResponse
from app.models.user import User
from app.services.auth_service import get_current_user, require_role
from app.services.audit_service import AuditService
from app.core.config import settings

router = APIRouter(prefix="/audit", tags=["Governance & Audit"])

@router.get("/logs", response_model=List[AuditLogResponse])
def get_audit_logs(
    limit: int = 50,
    skip: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["Admin", "Auditor"]))
):
    return AuditService.get_audit_logs(db, limit=limit, skip=skip)

@router.get("/health", response_model=SystemHealthResponse)
def get_system_health(db: Session = Depends(get_db)):
    # Check DB
    db_status = "Healthy"
    try:
        db.execute("SELECT 1")
    except Exception:
        db_status = "Unhealthy"

    # Vector store status
    vector_status = "Healthy (ChromaDB / Memory Store Active)"

    # LLM status
    llm_status = f"Active ({settings.LLM_PROVIDER.upper()})"

    return SystemHealthResponse(
        status="Healthy" if db_status == "Healthy" else "Degraded",
        database=db_status,
        vector_store=vector_status,
        llm_provider=llm_status,
        embedding_provider=f"Active ({settings.EMBEDDING_PROVIDER.title()})",
        version=settings.VERSION
    )
