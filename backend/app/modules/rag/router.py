from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from typing import List, Optional
from app.core.security import get_current_user, TokenPayload, require_role
from app.modules.rag.schemas import (
    KnowledgeFormRequest, 
    KnowledgeListResponse, 
    RAGSearchRequest, 
    RAGSearchResponse,
    RAGChunkResult,
    ExtractKeywordsRequest,
    ExtractKeywordsResponse,
)
from app.modules.rag.rag_service import qdrant_rag_service, extract_text_from_file_bytes

router = APIRouter(prefix="/rag", tags=["RAG & Knowledge Management"])

@router.get("/knowledge", response_model=KnowledgeListResponse)
def list_knowledge_items(current_user: TokenPayload = Depends(require_role(["doctor", "admin"]))):
    """Lists all indexed medical knowledge items and total Qdrant vector count."""
    res = qdrant_rag_service.list_knowledge_items()
    return KnowledgeListResponse(
        total_items=res["total_items"],
        total_vectors=res["total_vectors"],
        items=res["items"]
    )

@router.post("/knowledge")
def add_knowledge_item(
    request: KnowledgeFormRequest,
    current_user: TokenPayload = Depends(require_role(["doctor", "admin"]))
):
    """Web Form Data Ingestion: Submits new medical knowledge directly into Qdrant vector store."""
    doc_dict = request.dict()
    added_doc = qdrant_rag_service.add_knowledge_item(doc_dict)
    return {
        "status": "success",
        "message": f"Successfully ingested '{added_doc['title']}' into Qdrant vector store",
        "item": added_doc
    }

@router.post("/upload-doc")
async def upload_document_file(
    file: UploadFile = File(...),
    category: str = Form("document"),
    specialty: str = Form("General Medicine"),
    current_user: TokenPayload = Depends(require_role(["doctor", "admin"]))
):
    """Document File Upload: Uploads .pdf, .docx, .doc, .txt, .md, .json files and indexes content into Qdrant with Generative AI keyword extraction."""
    content_bytes = await file.read()
    raw_text = extract_text_from_file_bytes(file.filename, content_bytes)

    ingested_doc = qdrant_rag_service.ingest_uploaded_file(
        filename=file.filename,
        raw_content=raw_text,
        category=category,
        specialty=specialty
    )
    
    return {
        "status": "success",
        "message": f"File '{file.filename}' uploaded, keywords extracted by Generative AI, and indexed into Qdrant ({ingested_doc['chunks_count']} chunks)",
        "item": ingested_doc,
        "extracted_keywords": ingested_doc.get("keywords", [])
    }

@router.post("/extract-keywords", response_model=ExtractKeywordsResponse)
def extract_keywords_from_content(
    request: ExtractKeywordsRequest,
    current_user: TokenPayload = Depends(require_role(["doctor", "admin"]))
):
    """Uses Generative AI LLM to analyze text and extract relevant clinical keywords."""
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Konten teks tidak boleh kosong.")
    
    keywords = qdrant_rag_service.extract_keywords(
        text=request.text,
        title=request.title,
        max_keywords=request.max_keywords or 10
    )
    return ExtractKeywordsResponse(
        status="success",
        keywords=keywords,
        count=len(keywords)
    )


@router.delete("/knowledge/{item_id}")
def delete_knowledge_item(
    item_id: str,
    current_user: TokenPayload = Depends(require_role(["doctor", "admin"]))
):
    """Deletes a knowledge item and its vector points from Qdrant."""
    success = qdrant_rag_service.delete_knowledge_item(item_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Knowledge item '{item_id}' not found")
    return {"status": "success", "message": f"Deleted item '{item_id}' from Qdrant vector collection"}

@router.post("/search", response_model=RAGSearchResponse)
def execute_rag_search(
    request: RAGSearchRequest,
    current_user: TokenPayload = Depends(require_role(["doctor", "admin"]))
):
    """Direct Qdrant RAG Vector Search & Reranking execution."""
    results = qdrant_rag_service.search(
        query=request.query,
        top_k=request.top_k,
        category_filter=request.category_filter,
        similarity_threshold=request.similarity_threshold or 0.5
    )
    
    formatted_chunks = []
    for item in results:
        payload = item["payload"]
        formatted_chunks.append(
            RAGChunkResult(
                title=payload["title"],
                category=payload["category"].upper(),
                specialty=payload["specialty"],
                icd10_code=payload.get("icd10_code"),
                rxnorm_code=payload.get("rxnorm_code"),
                evidence_level=payload.get("evidence_level"),
                reranked_score=item["reranked_score"],
                boost_applied=item["boost_applied"],
                chunk_snippet=payload["chunk_text"],
                vector_score=item.get("vector_score"),
                bm25_score=item.get("bm25_score")
            )
        )
        
    return RAGSearchResponse(
        status="success",
        query=request.query,
        results_count=len(formatted_chunks),
        chunks=formatted_chunks
    )
