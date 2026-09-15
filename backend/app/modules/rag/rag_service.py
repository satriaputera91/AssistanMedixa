import os
import math
import re
import io
import logging
# pyrefly: ignore [missing-import]
import numpy as np
from datetime import datetime
from typing import List, Dict, Any, Optional

# pyrefly: ignore [missing-import]
from qdrant_client import QdrantClient
# pyrefly: ignore [missing-import]
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue

from app.core.config import settings

logger = logging.getLogger(__name__)

try:
    # pyrefly: ignore [missing-import]
    from google import genai
    HAS_GOOGLE_GENAI = True
except ImportError:
    HAS_GOOGLE_GENAI = False


# ==============================================================================
# DOCUMENT TEXT EXTRACTOR (PDF, DOCX, TXT, MD, JSON, CSV)
# ==============================================================================
def extract_text_from_file_bytes(filename: str, content_bytes: bytes) -> str:
    """Extracts text content from various file formats (.pdf, .docx, .doc, .txt, .md, .json, .csv)."""
    ext = os.path.splitext(filename)[1].lower()

    if ext == ".pdf":
        try:
            from pypdf import PdfReader
            reader = PdfReader(io.BytesIO(content_bytes))
            pages_text = []
            for idx, page in enumerate(reader.pages):
                page_text = page.extract_text() or ""
                if page_text.strip():
                    pages_text.append(f"### Halaman {idx + 1}\n{page_text.strip()}")
            if pages_text:
                return "\n\n".join(pages_text)
            return "Tidak ada teks yang dapat diekstrak dari dokumen PDF ini."
        except Exception as e:
            logger.error("Error reading PDF file %s: %s", filename, e)
            return f"Dokumen PDF: {filename}\nCatatan: Gagal memproses teks PDF secara langsung ({str(e)})."

    elif ext in (".docx", ".doc"):
        try:
            from docx import Document
            doc = Document(io.BytesIO(content_bytes))
            sections = []
            for p in doc.paragraphs:
                txt = p.text.strip()
                if txt:
                    sections.append(txt)
            for t_idx, table in enumerate(doc.tables):
                table_lines = []
                for row in table.rows:
                    row_cells = [c.text.strip() for c in row.cells if c.text.strip()]
                    if row_cells:
                        table_lines.append(" | ".join(row_cells))
                if table_lines:
                    sections.append(f"### Tabel {t_idx + 1}\n" + "\n".join(table_lines))
            if sections:
                return "\n\n".join(sections)
            return "Tidak ada teks yang dapat diekstrak dari dokumen Word (DOCX) ini."
        except Exception as e:
            logger.error("Error reading DOCX file %s: %s", filename, e)
            return f"Dokumen Word: {filename}\nCatatan: Gagal memproses teks DOCX secara langsung ({str(e)})."

    else:
        try:
            return content_bytes.decode("utf-8")
        except UnicodeDecodeError:
            return content_bytes.decode("latin-1", errors="ignore")


# ==============================================================================
# GEMINI LLM KEYWORD EXTRACTION ENGINE
# ==============================================================================
def extract_keywords_with_gemini(text: str, title: Optional[str] = None, max_keywords: int = 10) -> List[str]:
    """Extracts clinical and domain-specific keywords from medical text using Generative AI LLM."""
    api_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "")

    if api_key and HAS_GOOGLE_GENAI:
        try:
            client = genai.Client(api_key=api_key)
            prompt = (
                "Kamu adalah asisten AI medis untuk indexing sistem RAG rekam medis klinis. "
                "Tugasmu adalah menganalisis konten dokumen medis berikut dan mengekstrak 5-10 kata kunci (keywords / medical terms) terpenting, "
                "seperti nama penyakit, nama obat, istilah klinis, prosedur medis, temuan lab, atau konsep diagnosis terkait.\n\n"
                f"Judul Dokumen: {title or 'Tanpa Judul'}\n"
                f"Potongan Konten:\n{text[:4500]}\n\n"
                "Format respon: HANYA tuliskan kata kunci yang dipisahkan dengan tanda koma (contoh: diabetes melitus, metformin, hba1c, nefropati diabetik, insulin, hiperglikemia). "
                "JANGAN sertakan nomor urut, judul tambahan, atau kalimat pembuka/penutup."
            )
            response = client.models.generate_content(
                model=settings.GEMINI_MODEL_NAME or "gemini-2.0-flash",
                contents=prompt
            )
            if response and response.text:
                raw = response.text.strip()
                items = [
                    k.strip().strip("-*•").lower()
                    for k in re.split(r"[,;\n]+", raw)
                    if k.strip() and len(k.strip()) > 1
                ]
                if items:
                    seen = set()
                    unique_items = []
                    for item in items:
                        if item not in seen:
                            seen.add(item)
                            unique_items.append(item)
                    return unique_items[:max_keywords]
        except Exception as e:
            logger.warning("Gagal ekstraksi kata kunci dengan Generative AI: %s", e)

    # Fallback heuristic keyword extraction if LLM is unavailable
    words = [w.lower() for w in re.findall(r'[a-zA-Z0-9_-]+', f"{title or ''} {text}") if len(w) > 3]
    stopwords = {
        "yang", "untuk", "pada", "dari", "dalam", "dengan", "adalah", "ini", "itu", "akan",
        "dapat", "juga", "sebagai", "oleh", "file", "document", "metadata", "content", "overview",
        "halaman", "tabel", "atau", "serta", "saja", "telah", "lebih", "karena", "maka", "bisa",
        "tidak", "kategori", "spesialisasi", "upload", "uploaded"
    }
    filtered = [w for w in words if w not in stopwords]
    from collections import Counter
    counts = Counter(filtered)
    return [w for w, _ in counts.most_common(max_keywords)]


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
    """Generates 768-dimensional embeddings using Generative AI text-embedding-004 or dense vector encoder fallback."""
    
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
# QDRANT VECTOR RAG SERVICE WITH DYNAMIC KNOWLEDGE MANAGEMENT & BM25
# ==============================================================================
from app.modules.rag.bm25 import BM25Engine

class DedicatedQdrantRAGService:
    """Enterprise Qdrant Vector Database Service with BM25 Sparse Ranking, Hybrid Retrieval, Dynamic Knowledge Ingestion, and Threshold Filtering."""
    
    COLLECTION_NAME = "medical_knowledge_v1"
    
    def __init__(self):
        self.client = QdrantClient(":memory:")
        self.knowledge_store: Dict[str, Dict[str, Any]] = {}
        self.chunks_lookup: Dict[str, Dict[str, Any]] = {}
        self.bm25_engine = BM25Engine(k1=1.5, b=0.75, delta=0.5)
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
            self.add_knowledge_item(doc, rebuild_bm25=False)
        self._rebuild_bm25_index()

    def _rebuild_bm25_index(self):
        """Collects all chunks from all knowledge documents and indexes them in BM25."""
        all_chunks = []
        self.chunks_lookup = {}
        for doc in self.knowledge_store.values():
            chunks = doc.get("_cached_chunks")
            if not chunks:
                chunks = SemanticMarkdownChunker.chunk_document(doc)
                doc["_cached_chunks"] = chunks
            for ch in chunks:
                ch_id = ch["chunk_id"]
                all_chunks.append(ch)
                self.chunks_lookup[ch_id] = ch
        self.bm25_engine.index_chunks(all_chunks)
        logger.info(f"BM25 Index rebuilt with {len(all_chunks)} chunks across {len(self.knowledge_store)} knowledge docs.")

    def add_knowledge_item(self, doc: Dict[str, Any], rebuild_bm25: bool = True) -> Dict[str, Any]:
        """Ingests a new knowledge document into Qdrant collection and BM25 index."""
        item_id = doc.get("id") or f"kb-{doc.get('category', 'doc')[:3]}-{int(datetime.now().timestamp())}"
        doc["id"] = item_id
        if "created_at" not in doc:
            doc["created_at"] = datetime.now().isoformat()
            
        # Auto-extract keywords using Generative AI if keywords are empty or not provided
        if not doc.get("keywords"):
            doc["keywords"] = extract_keywords_with_gemini(
                text=doc.get("content", ""),
                title=doc.get("title"),
                max_keywords=10
            )
        if not doc.get("synonyms") and doc.get("title"):
            doc["synonyms"] = [doc["title"]] + (doc["keywords"][:3] if doc.get("keywords") else [])

        chunks = SemanticMarkdownChunker.chunk_document(doc)
        doc["chunks_count"] = len(chunks)
        doc["_cached_chunks"] = chunks
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

        if rebuild_bm25:
            self._rebuild_bm25_index()

        return doc

    def ingest_uploaded_file(
        self, 
        filename: str, 
        raw_content: str, 
        category: str = "document", 
        specialty: str = "General Medicine",
        custom_keywords: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Ingests raw file text upload (.pdf, .docx, .txt, .md, .json) into Qdrant knowledge base with Generative AI keyword extraction."""
        doc_title = os.path.splitext(filename)[0].replace("_", " ").replace("-", " ").title()
        
        # Extract keywords with Generative AI LLM
        if custom_keywords:
            keywords = custom_keywords
        else:
            keywords = extract_keywords_with_gemini(raw_content, title=doc_title, max_keywords=10)
            
        doc = {
            "title": doc_title,
            "category": category,
            "specialty": specialty,
            "icd10_code": None,
            "rxnorm_code": None,
            "loinc_code": None,
            "synonyms": [doc_title] + (keywords[:3] if keywords else []),
            "keywords": keywords,
            "evidence_level": f"Uploaded File ({filename})",
            "created_at": datetime.now().isoformat(),
            "content": f"### Overview & File Metadata\nFilename: {filename}\nUploaded: {datetime.now().isoformat()}\n\n### Document Content\n{raw_content}"
        }
        return self.add_knowledge_item(doc)

    def extract_keywords(self, text: str, title: Optional[str] = None, max_keywords: int = 10) -> List[str]:
        """Expose Generative AI LLM keyword extraction for API callers."""
        return extract_keywords_with_gemini(text, title=title, max_keywords=max_keywords)

    def delete_knowledge_item(self, item_id: str) -> bool:
        """Deletes a knowledge document and its vector points from Qdrant."""
        if item_id in self.knowledge_store:
            del self.knowledge_store[item_id]

            # Re-initialize & re-index remaining items
            self._initialize_collection()
            self.next_point_id = 1
            for doc in self.knowledge_store.values():
                chunks = SemanticMarkdownChunker.chunk_document(doc)
                doc["_cached_chunks"] = chunks
                points = []
                for chunk in chunks:
                    vec = GeminiEmbeddingEngine.get_embedding(chunk["chunk_text"], task_type="RETRIEVAL_DOCUMENT")
                    points.append(PointStruct(id=self.next_point_id, vector=vec, payload=chunk))
                    self.next_point_id += 1
                self.client.upsert(collection_name=self.COLLECTION_NAME, points=points)
            self._rebuild_bm25_index()
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

    def search(
        self, 
        query: str, 
        top_k: int = 3, 
        category_filter: Optional[str] = None,
        similarity_threshold: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Hybrid Qdrant Dense Vector + BM25 Sparse Ranking Search with Reranking and Threshold Filtering (> 0.5).
        Combines semantic embedding representation with exact term frequency BM25 relevance.
        """
        if not query or not query.strip():
            return []

        # 1. Dense Vector Search via Qdrant
        query_vec = GeminiEmbeddingEngine.get_embedding(query, task_type="RETRIEVAL_QUERY")
        search_results = self.client.query_points(
            collection_name=self.COLLECTION_NAME,
            query=query_vec,
            limit=30
        )
        
        # 2. Sparse Lexical Search via BM25
        bm25_norm_scores = self.bm25_engine.get_normalized_scores(query)
        bm25_top_results = self.bm25_engine.search(query, top_k=30)
        
        candidate_map: Dict[str, Dict[str, Any]] = {}
        
        # Add vector candidates
        for point in search_results.points:
            payload = point.payload or {}
            chunk_id = payload.get("chunk_id") or str(point.id)
            if category_filter and payload.get("category") != category_filter:
                continue
            
            v_score = max(float(point.score), 0.0)
            b_score = bm25_norm_scores.get(chunk_id, 0.0)
            
            candidate_map[chunk_id] = {
                "chunk_id": chunk_id,
                "vector_score": v_score,
                "bm25_score": b_score,
                "score": v_score,
                "payload": payload
            }

        # Add BM25 candidates that might have high lexical relevance
        for chunk_id, b_score, payload in bm25_top_results:
            if category_filter and payload.get("category") != category_filter:
                continue
            if chunk_id not in candidate_map:
                # If only found by BM25, calculate cosine vector score or baseline
                candidate_map[chunk_id] = {
                    "chunk_id": chunk_id,
                    "vector_score": 0.40,
                    "bm25_score": b_score,
                    "score": b_score,
                    "payload": payload or self.chunks_lookup.get(chunk_id, {})
                }
            else:
                candidate_map[chunk_id]["bm25_score"] = b_score

        candidates = list(candidate_map.values())
        
        # 3. Hybrid Re-ranking & Metadata Boosts
        reranked_results = self._rerank_candidates(query, candidates)

        # 4. Filter by Similarity Threshold (Threshold > 0.5)
        filtered_results = [
            item for item in reranked_results 
            if item.get("reranked_score", item.get("score", 0.0)) > similarity_threshold
        ]
        
        return filtered_results[:top_k]

    def _rerank_candidates(self, query: str, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        query_lower = query.lower()
        
        for item in candidates:
            payload = item["payload"]
            v_score = item.get("vector_score", 0.0)
            b_score = item.get("bm25_score", 0.0)
            
            boost = 0.0
            
            # Domain Metadata Boosts
            synonyms = [s.lower() for s in payload.get("synonyms", []) if isinstance(s, str)]
            title_lower = payload.get("title", "").lower()
            if any(syn in query_lower for syn in synonyms) or title_lower in query_lower:
                boost += 0.12
                
            icd = payload.get("icd10_code")
            rxnorm = payload.get("rxnorm_code")
            if icd and icd.lower() in query_lower:
                boost += 0.15
            if rxnorm and rxnorm.lower() in query_lower:
                boost += 0.15
                
            keywords = [k.lower() for k in payload.get("keywords", []) if isinstance(k, str)]
            matched_kw = sum(1 for kw in keywords if kw in query_lower)
            boost += min(matched_kw * 0.04, 0.12)
            
            # Hybrid Score formula: 0.45 * Vector + 0.40 * BM25 + Domain Boost
            # When both vector and BM25 match, confidence is significantly enhanced.
            hybrid_score = (0.45 * v_score) + (0.40 * b_score) + min(boost, 0.15)
            
            # Enhanced similarity score guaranteeing strong signal propagation
            final_similarity = max(
                hybrid_score,
                v_score * 0.90 + (boost * 0.5),
                b_score * 0.85 + (boost * 0.5)
            )
            final_similarity = round(min(final_similarity, 0.99), 4)

            item["reranked_score"] = final_similarity
            item["score"] = final_similarity
            item["vector_score"] = round(v_score, 4)
            item["bm25_score"] = round(b_score, 4)
            item["boost_applied"] = round(boost, 2)
            
        candidates.sort(key=lambda x: x["reranked_score"], reverse=True)
        return candidates


qdrant_rag_service = DedicatedQdrantRAGService()

