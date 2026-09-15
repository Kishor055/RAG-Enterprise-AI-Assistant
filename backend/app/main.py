import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import Base, engine, SessionLocal
from app.api.v1.router import api_router
from app.models.user import User
from app.models.document import KnowledgeBase, Document
from app.core.security import get_password_hash
from app.services.ingestion_service import IngestionService

# Create database tables automatically
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For flexible local dev access
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.on_event("startup")
def startup_db_seed():
    db = SessionLocal()
    try:
        # Seed default admin user
        admin = db.query(User).filter(User.email == "admin@enterprise.ai").first()
        if not admin:
            admin = User(
                email="admin@enterprise.ai",
                hashed_password=get_password_hash("AdminPass123!"),
                full_name="Enterprise Admin",
                role="Admin"
            )
            db.add(admin)

        # Seed default knowledge manager user
        mgr = db.query(User).filter(User.email == "manager@enterprise.ai").first()
        if not mgr:
            mgr = User(
                email="manager@enterprise.ai",
                hashed_password=get_password_hash("ManagerPass123!"),
                full_name="Finance Knowledge Manager",
                role="Knowledge Manager"
            )
            db.add(mgr)

        # Seed standard employee user
        emp = db.query(User).filter(User.email == "employee@enterprise.ai").first()
        if not emp:
            emp = User(
                email="employee@enterprise.ai",
                hashed_password=get_password_hash("EmployeePass123!"),
                full_name="Standard Employee",
                role="Standard User"
            )
            db.add(emp)

        db.commit()

        # Seed default Knowledge Base
        kb = db.query(KnowledgeBase).filter(KnowledgeBase.name == "Corporate Policies & Compliance").first()
        if not kb:
            kb = KnowledgeBase(
                name="Corporate Policies & Compliance",
                description="General enterprise security, HR policies, travel reimbursement rules, and compliance standards.",
                owner_id=admin.id,
                access_level="Public"
            )
            db.add(kb)
            db.commit()
            db.refresh(kb)

        # Seed sample enterprise policy document
        sample_doc = db.query(Document).filter(Document.title == "Enterprise Remote Work & Security Policy 2026").first()
        if not sample_doc:
            sample_text = (
                "ENTERPRISE REMOTE WORK & SECURITY POLICY 2026\n"
                "Section 1: General Guidelines & Eligibility\n"
                "All full-time employees are eligible for hybrid remote work up to 3 days per week upon manager approval. "
                "Remote work must be conducted using company-issued laptops equipped with full disk encryption.\n\n"
                "Section 2: Data Confidentiality & Access Control\n"
                "Employees must never store enterprise customer data on personal devices or unsecured USB drives. "
                "Access to confidential financial reports is strictly restricted to authorized role-based personnel (Finance Managers & Admins).\n\n"
                "Section 3: Travel & Expense Reimbursement Policy\n"
                "Business travel expenses including flights, hotel lodging up to $250/night, and meals up to $75/day must be submitted within 14 days of completion. "
                "Receipts are mandatory for all transactions exceeding $25.\n\n"
                "Section 4: Incident Response & Security Breaches\n"
                "In case of a lost laptop or suspicious phishing email, employees must notify the Security Operations Center (SOC) within 1 hour."
            )
            file_path = os.path.join(settings.UPLOAD_DIR, "seed_policy_2026.txt")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(sample_text)

            sample_doc = Document(
                id="doc_seed_policy_2026",
                title="Enterprise Remote Work & Security Policy 2026",
                file_name="seed_policy_2026.txt",
                file_path=file_path,
                file_type="txt",
                file_size=len(sample_text),
                knowledge_base_id=kb.id,
                owner_id=admin.id,
                status="Pending",
                is_public=True,
                allowed_roles="Admin,Knowledge Manager,Standard User"
            )
            db.add(sample_doc)
            db.commit()

            # Process ingestion for seed document
            try:
                ingestor = IngestionService()
                ingestor.process_document(db, sample_doc.id)
            except Exception:
                pass

        # Ensure vector store is loaded for all documents in DB
        try:
            ingestor = IngestionService()
            all_docs = db.query(Document).all()
            for d in all_docs:
                if d.status == "Indexed" or d.status == "Pending":
                    ingestor.process_document(db, d.id)
        except Exception:
            pass

    finally:
        db.close()


@app.get("/")
def root():
    return {
        "message": "RAG Enterprise AI Assistant API is operational.",
        "docs_url": "/api/v1/openapi.json",
        "health_check": "/api/v1/audit/health"
    }
