from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class RAGQueryRequest(BaseModel):
    query: str
    knowledge_base_ids: Optional[List[str]] = None
    top_k: int = 4
    temperature: float = 0.2

class SourceCitation(BaseModel):
    citation_id: int
    document_id: str
    document_title: str
    file_name: str
    page_number: int
    snippet: str
    similarity_score: float

class RAGQueryResponse(BaseModel):
    query: str
    answer: str
    citations: List[SourceCitation]
    retrieved_chunk_count: int
    execution_time_ms: float
    is_flagged_prompt_injection: bool = False
