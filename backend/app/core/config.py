import os
from typing import List, Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "RAG Enterprise AI Assistant"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = "rag_enterprise_secret_key_super_secure_change_in_production_2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Database
    DATABASE_URL: str = "sqlite:///./rag_enterprise.db"
    
    # Vector DB Settings
    VECTOR_DB_TYPE: str = "chroma"  # "chroma" or "memory"
    CHROMA_PERSIST_DIRECTORY: str = "./chroma_db"
    
    # LLM Settings
    LLM_PROVIDER: str = "gemini"  # "gemini", "openai", or "fallback"
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY", "")
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", "")
    
    # Embedding Settings
    EMBEDDING_PROVIDER: str = "local"  # "local", "openai", "gemini"
    EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"
    
    # Document Storage
    UPLOAD_DIR: str = "./storage/documents"
    MAX_UPLOAD_SIZE_MB: int = 50
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"]
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()

# Ensure required directories exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.CHROMA_PERSIST_DIRECTORY, exist_ok=True)
