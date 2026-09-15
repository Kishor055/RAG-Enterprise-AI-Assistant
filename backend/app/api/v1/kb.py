from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.document import KnowledgeBaseCreate, KnowledgeBaseResponse
from app.models.document import KnowledgeBase, Document
from app.models.user import User
from app.services.auth_service import get_current_user, require_role

router = APIRouter(prefix="/kb", tags=["Knowledge Base"])

@router.post("/", response_model=KnowledgeBaseResponse, status_code=status.HTTP_201_CREATED)
def create_knowledge_base(
    kb_in: KnowledgeBaseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["Admin", "Knowledge Manager"]))
):
    kb = KnowledgeBase(
        name=kb_in.name,
        description=kb_in.description,
        owner_id=current_user.id,
        access_level=kb_in.access_level
    )
    db.add(kb)
    db.commit()
    db.refresh(kb)
    return KnowledgeBaseResponse(
        id=kb.id,
        name=kb.name,
        description=kb.description,
        access_level=kb.access_level,
        owner_id=kb.owner_id,
        created_at=kb.created_at,
        document_count=0
    )

@router.get("/", response_model=List[KnowledgeBaseResponse])
def list_knowledge_bases(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(KnowledgeBase)
    if current_user.role != "Admin":
        query = query.filter(
            (KnowledgeBase.access_level == "Public") | 
            (KnowledgeBase.owner_id == current_user.id)
        )
    kbs = query.all()
    
    results = []
    for kb in kbs:
        doc_count = db.query(Document).filter(Document.knowledge_base_id == kb.id).count()
        results.append(KnowledgeBaseResponse(
            id=kb.id,
            name=kb.name,
            description=kb.description,
            access_level=kb.access_level,
            owner_id=kb.owner_id,
            created_at=kb.created_at,
            document_count=doc_count
        ))
    return results

@router.delete("/{kb_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_knowledge_base(
    kb_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["Admin", "Knowledge Manager"]))
):
    kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == kb_id).first()
    if not kb:
        raise HTTPException(status_code=404, detail="Knowledge base not found.")
    
    if current_user.role != "Admin" and kb.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this knowledge base.")

    db.delete(kb)
    db.commit()
    return None
