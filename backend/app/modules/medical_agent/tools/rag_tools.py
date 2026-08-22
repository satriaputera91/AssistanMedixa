from typing import Dict, Any, List, Optional
from app.modules.rag.rag_service import qdrant_rag_service

def tool_vector_rag_search(query: str, top_k: int = 3, category_filter: Optional[str] = None) -> List[Dict[str, Any]]:
    """Performs semantic vector search across validated medical guidelines and literature using Qdrant."""
    if not query or not query.strip():
        return []
    try:
        results = qdrant_rag_service.search(query=query, top_k=top_k, category_filter=category_filter)
        formatted_chunks = []
        for r in results:
            payload = r.get("payload", {})
            snippet = payload.get("chunk_text") or payload.get("content", "")
            formatted_chunks.append({
                "title": payload.get("title", "Clinical Knowledge Item"),
                "category": payload.get("category", "General"),
                "specialty": payload.get("specialty", "General Medicine"),
                "icd10_code": payload.get("icd10_code"),
                "rxnorm_code": payload.get("rxnorm_code"),
                "evidence_level": payload.get("evidence_level"),
                "chunk_snippet": snippet[:400],
                "parent_content": payload.get("parent_content") or payload.get("content") or snippet,
                "score": r.get("score", 0.85),
                "reranked_score": r.get("reranked_score", 0.90)
            })
        return formatted_chunks
    except Exception:
        return []

def tool_get_clinical_literature_summary(query: str) -> str:
    """Retrieves synthesized medical evidence from guidelines (KDIGO, ADA, AHA/ACC, PERKENI)."""
    if not query or not query.strip():
        return ""
    try:
        chunks = tool_vector_rag_search(query, top_k=2)
        if chunks:
            summaries = [f"• {c['title']} ({c['specialty']}): {c['chunk_snippet']}" for c in chunks]
            return "\n".join(summaries)
    except Exception:
        pass
    return ""
