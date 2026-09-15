import os
import shutil
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status, BackgroundTasks
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.schemas.document import DocumentResponse, DocumentPermissionsUpdate
from app.models.document import Document, KnowledgeBase
from app.models.user import User
from app.services.auth_service import get_current_user, require_role
from app.services.ingestion_service import IngestionService

router = APIRouter(prefix="/documents", tags=["Document Management"])
ingestion_service = IngestionService()

@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    knowledge_base_id: str = Form(...),
    is_public: bool = Form(True),
    allowed_roles: Optional[str] = Form("Admin,Knowledge Manager,Standard User"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["Admin", "Knowledge Manager"]))
):
    kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == knowledge_base_id).first()
    if not kb:
        raise HTTPException(status_code=404, detail="Target Knowledge Base not found.")

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".pdf", ".docx", ".txt", ".md", ".csv"]:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file extension '{ext}'. Allowed: .pdf, .docx, .txt, .md, .csv"
        )

    file_id = str(uuid.uuid4())
    safe_filename = f"{file_id}_{file.filename}"
    file_path = os.path.join(settings.UPLOAD_DIR, safe_filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_size = os.path.getsize(file_path)

    doc = Document(
        id=file_id,
        title=os.path.splitext(file.filename)[0].replace("_", " ").title(),
        file_name=file.filename,
        file_path=file_path,
        file_type=ext.replace(".", ""),
        file_size=file_size,
        knowledge_base_id=knowledge_base_id,
        owner_id=current_user.id,
        status="Pending",
        is_public=is_public,
        allowed_roles=allowed_roles or "Admin,Knowledge Manager,Standard User"
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    # Process ingestion synchronously for fast small files, or queue in background
    try:
        doc = ingestion_service.process_document(db, doc.id)
    except Exception as e:
        doc.status = "Failed"
        doc.error_message = str(e)
        db.commit()

    return doc

@router.get("/", response_model=List[DocumentResponse])
def list_documents(
    knowledge_base_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Document)
    if knowledge_base_id:
        query = query.filter(Document.knowledge_base_id == knowledge_base_id)
    
    if current_user.role != "Admin":
        query = query.filter(
            (Document.is_public == True) | 
            (Document.owner_id == current_user.id)
        )
    return query.order_by(Document.created_at.desc()).all()

@router.patch("/{doc_id}/permissions", response_model=DocumentResponse)
def update_document_permissions(
    doc_id: str,
    perm_in: DocumentPermissionsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["Admin", "Knowledge Manager"]))
):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    doc.is_public = perm_in.is_public
    doc.allowed_roles = ",".join(perm_in.allowed_roles)
    db.commit()
    db.refresh(doc)

    # Re-index chunks in vector store with updated metadata
    try:
        ingestion_service.vector_store.delete_by_document_id(doc.id)
        ingestion_service.process_document(db, doc.id)
    except Exception:
        pass

    return doc

@router.post("/{doc_id}/reindex", response_model=DocumentResponse)
def reindex_document(
    doc_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["Admin", "Knowledge Manager"]))
):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    
    ingestion_service.vector_store.delete_by_document_id(doc.id)
    doc = ingestion_service.process_document(db, doc.id)
    return doc

@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    doc_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["Admin", "Knowledge Manager"]))
):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    # Remove vector store records
    ingestion_service.vector_store.delete_by_document_id(doc.id)

    # Delete disk file if exists
    if os.path.exists(doc.file_path):
        try:
            os.remove(doc.file_path)
        except Exception:
            pass

    db.delete(doc)
    db.commit()
    return None
