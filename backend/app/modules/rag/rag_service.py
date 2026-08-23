import os
import math
import re
# pyrefly: ignore [missing-import]
import numpy as np
from datetime import datetime
from typing import List, Dict, Any, Optional
# pyrefly: ignore [missing-import]
from qdrant_client import QdrantClient
# pyrefly: ignore [missing-import]
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue

from app.core.config import settings

try:
    # pyrefly: ignore [missing-import]
    from google import genai
    HAS_GOOGLE_GENAI = True
except ImportError:
    HAS_GOOGLE_GENAI = False

# ==============================================================================
# PRE-LOADED MEDICAL KNOWLEDGE BASE DOCUMENTS (Imported from initial_knowledge.py)
# ==============================================================================
from app.modules.rag.initial_knowledge import INITIAL_KNOWLEDGE_BASE



# ==============================================================================
# SEMANTIC MARKDOWN CHUNKER
# ==============================================================================
class SemanticMarkdownChunker:
    """Splits medical documents along section headers with overlap and parent metadata header injection."""
    
    @staticmethod
    def chunk_document(doc: Dict[str, Any], max_chunk_words: int = 250, overlap_words: int = 40) -> List[Dict[str, Any]]:
        raw_content = doc.get("content", "")
        sections = raw_content.split("### ")
        chunks = []
        
        meta_header = (
            f"[DOCUMENT METADATA]\n"
            f"Title: {doc['title']} | Category: {doc['category'].upper()} | Specialty: {doc['specialty']}\n"
            f"ICD-10: {doc.get('icd10_code') or 'N/A'} | RxNorm: {doc.get('rxnorm_code') or 'N/A'}\n"
            f"Synonyms: {', '.join(doc.get('synonyms', []))}\n"
            f"Keywords: {', '.join(doc.get('keywords', []))}\n"
            f"Evidence: {doc.get('evidence_level')}\n"
            f"--------------------------------------------------\n"
        )

        chunk_idx = 1
        for sec in sections:
            if not sec.strip():
                continue
                
            sec_text = "### " + sec.strip()
            words = sec_text.split()
            
            if len(words) <= max_chunk_words:
                chunks.append({
                    "chunk_id": f"{doc['id']}-c{chunk_idx}",
                    "parent_id": doc["id"],
                    "title": doc["title"],
                    "category": doc["category"],
                    "specialty": doc["specialty"],
                    "icd10_code": doc.get("icd10_code"),
                    "rxnorm_code": doc.get("rxnorm_code"),
                    "loinc_code": doc.get("loinc_code"),
                    "synonyms": doc.get("synonyms", []),
                    "keywords": doc.get("keywords", []),
                    "evidence_level": doc.get("evidence_level"),
                    "chunk_text": meta_header + sec_text,
                    "parent_content": raw_content
                })
                chunk_idx += 1
            else:
                for i in range(0, len(words), max_chunk_words - overlap_words):
                    sub_words = words[i:i + max_chunk_words]
                    sub_text = " ".join(sub_words)
                    chunks.append({
                        "chunk_id": f"{doc['id']}-c{chunk_idx}",
                        "parent_id": doc["id"],
                        "title": doc["title"],
                        "category": doc["category"],
                        "specialty": doc["specialty"],
                        "icd10_code": doc.get("icd10_code"),
                        "rxnorm_code": doc.get("rxnorm_code"),
                        "loinc_code": doc.get("loinc_code"),
                        "synonyms": doc.get("synonyms", []),
                        "keywords": doc.get("keywords", []),
                        "evidence_level": doc.get("evidence_level"),
                        "chunk_text": meta_header + sub_text,
                        "parent_content": raw_content
                    })
                    chunk_idx += 1
                    
        return chunks


# ==============================================================================
# GEMINI EMBEDDING ENGINE (text-embedding-004)
# ==============================================================================
class GeminiEmbeddingEngine:
    """Generates 768-dimensional embeddings using Gemini text-embedding-004 or dense vector encoder fallback."""
    
    VECTOR_DIM = 768
    
    @classmethod
    def get_embedding(cls, text: str, task_type: str = "RETRIEVAL_QUERY") -> List[float]:
        api_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "")
        
        if api_key and HAS_GOOGLE_GENAI:
            try:
                client = genai.Client(api_key=api_key)
                response = client.models.embed_content(
                    model="text-embedding-004",
                    contents=text
                )
                if response and hasattr(response, "embedding"):
                    return response.embedding.values
            except Exception:
                pass

        return cls._generate_fallback_dense_vector(text)

    @classmethod
    def _generate_fallback_dense_vector(cls, text: str) -> List[float]:
        """Generates a deterministic semantic feature vector using token hash projections."""
        words = re.findall(r'\w+', text.lower())
        vec = np.zeros(cls.VECTOR_DIM, dtype=np.float32)
        if not words:
            vec[0] = 1.0
            return vec.tolist()
        
        for w in words:
            idx = abs(hash(w)) % cls.VECTOR_DIM
            vec[idx] += 1.0
            for i in range(max(0, len(w) - 2)):
                tri = w[i:i+3]
                sub_idx = abs(hash(tri)) % cls.VECTOR_DIM
                vec[sub_idx] += 0.3
                
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()


# ==============================================================================
# QDRANT VECTOR RAG SERVICE WITH DYNAMIC KNOWLEDGE MANAGEMENT
# ==============================================================================
class DedicatedQdrantRAGService:
    """Enterprise Qdrant Vector Database Service with Dynamic Knowledge Ingestion, File Upload, and Reranking."""
    
    COLLECTION_NAME = "medical_knowledge_v1"
    
    def __init__(self):
        self.client = QdrantClient(":memory:")
        self.knowledge_store: Dict[str, Dict[str, Any]] = {}
        self.next_point_id = 1
        self._initialize_collection()
        self._seed_initial_knowledge()

    def _initialize_collection(self):
        self.client.recreate_collection(
            collection_name=self.COLLECTION_NAME,
            vectors_config=VectorParams(
                size=GeminiEmbeddingEngine.VECTOR_DIM,
                distance=Distance.COSINE
            )
        )

    def _seed_initial_knowledge(self):
        for doc in INITIAL_KNOWLEDGE_BASE:
            self.add_knowledge_item(doc)

    def add_knowledge_item(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """Ingests a new knowledge document into Qdrant collection."""
        item_id = doc.get("id") or f"kb-{doc.get('category', 'doc')[:3]}-{int(datetime.now().timestamp())}"
        doc["id"] = item_id
        if "created_at" not in doc:
            doc["created_at"] = datetime.now().isoformat()
            
        chunks = SemanticMarkdownChunker.chunk_document(doc)
        doc["chunks_count"] = len(chunks)
        self.knowledge_store[item_id] = doc
        
        points = []
        for chunk in chunks:
            vec = GeminiEmbeddingEngine.get_embedding(chunk["chunk_text"], task_type="RETRIEVAL_DOCUMENT")
            points.append(
                PointStruct(
                    id=self.next_point_id,
                    vector=vec,
                    payload=chunk
                )
            )
            self.next_point_id += 1
            
        self.client.upsert(
            collection_name=self.COLLECTION_NAME,
            points=points
        )
        return doc

    def ingest_uploaded_file(
        self, 
        filename: str, 
        raw_content: str, 
        category: str = "document", 
        specialty: str = "General Medicine"
    ) -> Dict[str, Any]:
        """Ingests raw file text upload (.txt, .md, .json) into Qdrant knowledge base."""
        doc_title = os.path.splitext(filename)[0].replace("_", " ").replace("-", " ").title()
        
        doc = {
            "title": doc_title,
            "category": category,
            "specialty": specialty,
            "icd10_code": None,
            "rxnorm_code": None,
            "loinc_code": None,
            "synonyms": [doc_title],
            "keywords": [w.lower() for w in re.findall(r'\w+', doc_title) if len(w) > 3],
            "evidence_level": f"Uploaded File ({filename})",
            "created_at": datetime.now().isoformat(),
            "content": f"### Overview & File Metadata\nFilename: {filename}\nUploaded: {datetime.now().isoformat()}\n\n### Document Content\n{raw_content}"
        }
        return self.add_knowledge_item(doc)

    def delete_knowledge_item(self, item_id: str) -> bool:
        """Deletes a knowledge document and its vector points from Qdrant."""
        if item_id in self.knowledge_store:
            del self.knowledge_store[item_id]
            # Re-initialize & re-index remaining items
            self._initialize_collection()
            self.next_point_id = 1
            for doc in self.knowledge_store.values():
                chunks = SemanticMarkdownChunker.chunk_document(doc)
                points = []
                for chunk in chunks:
                    vec = GeminiEmbeddingEngine.get_embedding(chunk["chunk_text"], task_type="RETRIEVAL_DOCUMENT")
                    points.append(PointStruct(id=self.next_point_id, vector=vec, payload=chunk))
                    self.next_point_id += 1
                self.client.upsert(collection_name=self.COLLECTION_NAME, points=points)
            return True
        return False

    def list_knowledge_items(self) -> Dict[str, Any]:
        """Lists all indexed knowledge documents and metrics."""
        items = list(self.knowledge_store.values())
        total_vectors = sum(item.get("chunks_count", 1) for item in items)
        return {
            "total_items": len(items),
            "total_vectors": total_vectors,
            "items": items
        }

    def search(self, query: str, top_k: int = 3, category_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Two-Stage Qdrant Retrieval Engine with Reranking."""
        query_vec = GeminiEmbeddingEngine.get_embedding(query, task_type="RETRIEVAL_QUERY")
        
        search_results = self.client.query_points(
            collection_name=self.COLLECTION_NAME,
            query=query_vec,
            limit=20
        )
        
        candidates = []
        for point in search_results.points:
            payload = point.payload or {}
            if category_filter and payload.get("category") != category_filter:
                continue
            candidates.append({
                "score": float(point.score),
                "payload": payload
            })
            
        reranked_results = self._rerank_candidates(query, candidates)
        return reranked_results[:top_k]

    def _rerank_candidates(self, query: str, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        query_lower = query.lower()
        
        for item in candidates:
            payload = item["payload"]
            base_score = item["score"]
            boost = 0.0
            
            synonyms = [s.lower() for s in payload.get("synonyms", [])]
            title_lower = payload.get("title", "").lower()
            if any(syn in query_lower for syn in synonyms) or title_lower in query_lower:
                boost += 0.15
                
            icd = payload.get("icd10_code")
            rxnorm = payload.get("rxnorm_code")
            if icd and icd.lower() in query_lower:
                boost += 0.20
            if rxnorm and rxnorm.lower() in query_lower:
                boost += 0.20
                
            keywords = [k.lower() for k in payload.get("keywords", [])]
            matched_kw = sum(1 for kw in keywords if kw in query_lower)
            boost += min(matched_kw * 0.05, 0.15)
            
            item["reranked_score"] = round(min(base_score + boost, 0.99), 4)
            item["boost_applied"] = round(boost, 2)
            
        candidates.sort(key=lambda x: x["reranked_score"], reverse=True)
        return candidates


qdrant_rag_service = DedicatedQdrantRAGService()
