from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class KnowledgeFormRequest(BaseModel):
    title: str
    category: str  # "disease", "medicine", "terminology"
    specialty: str = "General Medicine"
    icd10_code: Optional[str] = None
    rxnorm_code: Optional[str] = None
    loinc_code: Optional[str] = None
    synonyms: Optional[List[str]] = []
    keywords: Optional[List[str]] = []
    evidence_level: Optional[str] = "Clinical Consensus 2026"
    content: str

class KnowledgeItemSchema(BaseModel):
    id: str
    title: str
    category: str
    specialty: str
    icd10_code: Optional[str] = None
    rxnorm_code: Optional[str] = None
    loinc_code: Optional[str] = None
    synonyms: List[str] = []
    keywords: List[str] = []
    evidence_level: Optional[str] = None
    chunks_count: int
    created_at: str

class KnowledgeListResponse(BaseModel):
    total_items: int
    total_vectors: int
    items: List[KnowledgeItemSchema]

class RAGSearchRequest(BaseModel):
    query: str
    top_k: int = 3
    category_filter: Optional[str] = None
    similarity_threshold: Optional[float] = 0.5

class RAGChunkResult(BaseModel):
    title: str
    category: str
    specialty: str
    icd10_code: Optional[str] = None
    rxnorm_code: Optional[str] = None
    evidence_level: Optional[str] = None
    reranked_score: float
    boost_applied: float
    chunk_snippet: str
    vector_score: Optional[float] = None
    bm25_score: Optional[float] = None

class RAGSearchResponse(BaseModel):
    status: str
    query: str
    results_count: int
    chunks: List[RAGChunkResult]

class ExtractKeywordsRequest(BaseModel):
    text: str
    title: Optional[str] = None
    max_keywords: Optional[int] = 10

class ExtractKeywordsResponse(BaseModel):
    status: str
    keywords: List[str]
    count: int

