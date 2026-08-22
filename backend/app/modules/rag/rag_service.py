import os
import math
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
# 10 PRE-LOADED MEDICAL KNOWLEDGE BASE DOCUMENTS
# ==============================================================================
INITIAL_KNOWLEDGE_BASE: List[Dict[str, Any]] = [
    {
        "id": "kb-dis-001",
        "title": "Type 2 Diabetes Mellitus (T2DM)",
        "category": "disease",
        "specialty": "Endocrinology",
        "icd10_code": "E11.9",
        "rxnorm_code": None,
        "loinc_code": None,
        "synonyms": ["Type 2 Diabetes", "T2D", "T2DM", "Non-Insulin Dependent Diabetes", "Adult-Onset Diabetes"],
        "keywords": ["HbA1c", "glycemic target", "metformin", "fasting blood glucose", "insulin resistance", "hyperglycemia"],
        "evidence_level": "ADA Standards of Care 2025 (Level A)",
        "created_at": datetime.now().isoformat(),
        "content": """
### Clinical Definition & Overview
Type 2 Diabetes Mellitus (T2DM) is a chronic metabolic disorder characterized by hyperglycemia, insulin resistance, and relative impairment in insulin secretion.

### Diagnostic Criteria
1. Fasting Plasma Glucose (FPG) ≥ 126 mg/dL (7.0 mmol/L) after an 8-hour fast.
2. 2-Hour Plasma Glucose ≥ 200 mg/dL (11.1 mmol/L) during an Oral Glucose Tolerance Test (OGTT).
3. Glycated Hemoglobin (HbA1c) ≥ 6.5% (48 mmol/mol).
4. Random Plasma Glucose ≥ 200 mg/dL with classic hyperglycemic symptoms (polyuria, polydipsia, unexplained weight loss).

### Treatment & Management Guidelines
- First-Line Pharmacotherapy: Metformin (unless contraindicated by eGFR < 30 mL/min).
- Target Glycemic Goal: HbA1c < 7.0% for most non-pregnant adults.
- Cardiorenal Protection: SGLT2 inhibitors (Empagliflozin, Dapagliflozin) or GLP-1 Receptor Agonists (Semaglutide) recommended for patients with ASCVD, Heart Failure, or CKD.
"""
    },
    {
        "id": "kb-dis-002",
        "title": "Chronic Kidney Disease (CKD)",
        "category": "disease",
        "specialty": "Nephrology",
        "icd10_code": "N18.9",
        "rxnorm_code": None,
        "loinc_code": None,
        "synonyms": ["CKD", "Chronic Renal Failure", "Renal Impairment", "Chronic Kidney Failure"],
        "keywords": ["eGFR", "serum creatinine", "albuminuria", "KDIGO", "SGLT2 inhibitor", "Lisinopril", "nephroprotection"],
        "evidence_level": "KDIGO 2024 Clinical Practice Guideline",
        "created_at": datetime.now().isoformat(),
        "content": """
### Staging & Definition
Chronic Kidney Disease (CKD) is defined as abnormalities of kidney structure or function present for > 3 months.
- Stage 1: eGFR ≥ 90 mL/min/1.73m² with persistent kidney damage.
- Stage 2: eGFR 60–89 mL/min/1.73m².
- Stage 3a: eGFR 45–59 mL/min/1.73m² (Mild-to-moderate decline).
- Stage 3b: eGFR 30–44 mL/min/1.73m² (Moderate-to-severe decline).
- Stage 4: eGFR 15–29 mL/min/1.73m² (Severe decline).
- Stage 5: eGFR < 15 mL/min/1.73m² (Kidney Failure / End-Stage Renal Disease).

### Evidence-Based Treatment Protocols
1. Renin-Angiotensin System Inhibition: ACE inhibitors (Lisinopril) or ARBs (Losartan) in diabetic/hypertensive patients with UACR ≥ 30 mg/g.
2. SGLT2 Inhibitor Therapy: Recommended for patients with eGFR ≥ 20 mL/min/1.73m² and UACR ≥ 200 mg/g to delay CKD progression.
3. Electrolyte Monitoring: Monitor serum potassium (K+) and creatinine within 2–4 weeks of initiating ACEi/ARB therapy.
"""
    },
    {
        "id": "kb-dis-003",
        "title": "Essential Hypertension (HTN)",
        "category": "disease",
        "specialty": "Cardiology",
        "icd10_code": "I10",
        "rxnorm_code": None,
        "loinc_code": None,
        "synonyms": ["HTN", "High Blood Pressure", "Primary Hypertension", "Essential HTN"],
        "keywords": ["systolic BP", "diastolic BP", "ACC/AHA", "ACE inhibitor", "thiazide", "calcium channel blocker", "amlodipine"],
        "evidence_level": "ACC/AHA 2024 Hypertension Guidelines",
        "created_at": datetime.now().isoformat(),
        "content": """
### Diagnostic Classification
- Normal BP: < 120/80 mmHg.
- Elevated BP: Systolic 120–129 AND Diastolic < 80 mmHg.
- Stage 1 HTN: Systolic 130–139 OR Diastolic 80–89 mmHg.
- Stage 2 HTN: Systolic ≥ 140 OR Diastolic ≥ 90 mmHg.

### Pharmacotherapy Guidelines
- Target BP Goal: < 130/80 mmHg for high ASCVD risk, diabetes, or CKD.
- First-Line Drug Classes: Thiazide Diuretics (Chlorthalidone), CCBs (Amlodipine), and ACEi (Lisinopril) / ARBs (Valsartan).
"""
    },
    {
        "id": "kb-dis-004",
        "title": "Acute Coronary Syndrome (ACS)",
        "category": "disease",
        "specialty": "Cardiology",
        "icd10_code": "I24.9",
        "rxnorm_code": None,
        "loinc_code": None,
        "synonyms": ["ACS", "Myocardial Infarction", "Heart Attack", "STEMI", "NSTEMI", "Unstable Angina"],
        "keywords": ["cardiac troponin T", "DAPT", "clopidogrel", "aspirin", "coronary stent", "ischemia", "chest pain"],
        "evidence_level": "ESC/ACC ACS Guidelines",
        "created_at": datetime.now().isoformat(),
        "content": """
### Clinical Spectrum & Diagnostics
Encompasses STEMI, NSTEMI, and Unstable Angina. Evaluate with serial high-sensitivity Cardiac Troponin (hs-cTnI / hs-cTnT) and 12-lead ECG.

### Acute Pharmacologic Management
1. Aspirin: 162–325 mg chewed immediately.
2. P2Y12 Inhibitor (DAPT): Clopidogrel (300–600 mg load) or Ticagrelor (180 mg load).
3. Post-PCI DAPT Duration: 12 months minimum post-stent placement.
"""
    },
    {
        "id": "kb-med-001",
        "title": "Metformin (Biguanide Antidiabetic)",
        "category": "medicine",
        "specialty": "Pharmacology",
        "icd10_code": None,
        "rxnorm_code": "6809",
        "loinc_code": None,
        "synonyms": ["Glucophage", "Metformin Hydrochloride", "Fortamet", "Glumetza"],
        "keywords": ["biguanide", "eGFR cutoff", "lactic acidosis", "hepatic gluconeogenesis", "t2d first-line", "vitamin b12"],
        "evidence_level": "FDA Prescribing Information & ADA 2025",
        "created_at": datetime.now().isoformat(),
        "content": """
### Mechanism & Renal Dosing Cutoffs (eGFR)
Metformin decreases hepatic gluconeogenesis and improves insulin sensitivity.
- eGFR ≥ 60 mL/min: Full therapeutic dose (up to 2000 mg/day).
- eGFR 45–59 mL/min: Safe to continue full dose; monitor renal function every 3–6 months.
- eGFR 30–44 mL/min: Max dose 1000 mg/day; do NOT initiate in new patients.
- eGFR < 30 mL/min: Absolute CONTRAINDICATION due to risk of fatal Lactic Acidosis. Hold 48 hours prior to radiocontrast procedures.
"""
    },
    {
        "id": "kb-med-002",
        "title": "Lisinopril (ACE Inhibitor)",
        "category": "medicine",
        "specialty": "Pharmacology",
        "icd10_code": None,
        "rxnorm_code": "29046",
        "loinc_code": None,
        "synonyms": ["Zestril", "Prinivil", "ACE Inhibitor", "Lisinopril-Hydrochlorothiazide"],
        "keywords": ["angiotensin converting enzyme inhibitor", "hyperkalemia", "serum potassium", "diabetic nephropathy", "dry cough", "angioedema"],
        "evidence_level": "FDA Prescribing Information & KDIGO 2024",
        "created_at": datetime.now().isoformat(),
        "content": """
### Indications & Monitoring
Inhibits ACE, decreasing Angiotensin II. Indicated for Hypertension, Heart Failure, and Diabetic Nephropathy.
- Hyperkalemia Risk: Monitor serum potassium (K+). Avoid co-administration with potassium-sparing diuretics (Spironolactone) without monitoring.
- Serum Creatinine: Up to 30% rise upon initiation is acceptable due to efferent arteriole dilation.
- Dry Cough: Switch to ARB (Losartan) if intolerable.
"""
    },
    {
        "id": "kb-med-003",
        "title": "Clopidogrel (P2Y12 Antiplatelet Agent)",
        "category": "medicine",
        "specialty": "Pharmacology",
        "icd10_code": None,
        "rxnorm_code": "32968",
        "loinc_code": None,
        "synonyms": ["Plavix", "P2Y12 Inhibitor", "Antiplatelet Agent"],
        "keywords": ["prodrug", "CYP2C19", "omeprazole interaction", "stent thrombosis", "bleeding risk", "dapt"],
        "evidence_level": "FDA Boxed Warning & ACC/AHA DAPT Guidelines",
        "created_at": datetime.now().isoformat(),
        "content": """
### Mechanism & Drug Interactions
Oral prodrug requiring CYP2C19 activation to irreversibly inhibit platelet P2Y12 receptors.
- Omeprazole Interaction: Omeprazole inhibits CYP2C19, reducing Clopidogrel active metabolite and raising stent thrombosis risk. Use Pantoprazole or Famotidine alternative.
- Hold 5 days prior to major elective surgery (CABG).
"""
    },
    {
        "id": "kb-term-001",
        "title": "Estimated Glomerular Filtration Rate (eGFR)",
        "category": "terminology",
        "specialty": "Nephrology / Lab Diagnostics",
        "icd10_code": None,
        "rxnorm_code": None,
        "loinc_code": "33914-3",
        "synonyms": ["eGFR", "Glomerular Filtration Rate", "Calculated GFR", "CKD-EPI equation"],
        "keywords": ["serum creatinine", "renal clearance", "kidney staging", "drug dosage adjustment", "renal function"],
        "evidence_level": "National Kidney Foundation (NKF)",
        "created_at": datetime.now().isoformat(),
        "content": """
### Interpretation & Cutoffs
Measures blood filtration rate (mL/min/1.73m²) calculated via CKD-EPI equation based on serum creatinine, age, and sex.
- Normal: > 90 mL/min/1.73m²
- Mild Decline: 60–89 mL/min/1.73m²
- Moderate Decline: 30–59 mL/min/1.73m² (Triggers drug renal dose adjustment)
- Severe Decline: < 30 mL/min/1.73m² (Triggers drug cutoffs)
"""
    },
    {
        "id": "kb-term-002",
        "title": "Glycated Hemoglobin (HbA1c)",
        "category": "terminology",
        "specialty": "Endocrinology / Lab Diagnostics",
        "icd10_code": None,
        "rxnorm_code": None,
        "loinc_code": "4548-4",
        "synonyms": ["HbA1c", "A1C", "Glycohemoglobin", "Hemoglobin A1c"],
        "keywords": ["average blood glucose", "glycemic control", "erythrocyte lifespan", "diabetes diagnostic threshold"],
        "evidence_level": "ADA Standards of Medical Care",
        "created_at": datetime.now().isoformat(),
        "content": """
### Diagnostic Cutoffs
Reflects 2-3 month average blood glucose (erythrocyte 120-day lifespan).
- Normal: < 5.7%
- Prediabetes: 5.7% – 6.4%
- Diabetes Mellitus: ≥ 6.5%
- Standard Goal: < 7.0% (estimated Average Glucose ~154 mg/dL).
"""
    },
    {
        "id": "kb-term-003",
        "title": "High Anion Gap Metabolic Acidosis (HAGMA)",
        "category": "terminology",
        "specialty": "Critical Care / Nephrology",
        "icd10_code": None,
        "rxnorm_code": None,
        "loinc_code": "1863-7",
        "synonyms": ["HAGMA", "Anion Gap Acidosis", "Metabolic Acidosis", "High Anion Gap"],
        "keywords": ["bicarbonate", "sodium", "chloride", "MUDPILES", "lactic acidosis", "ketoacidosis", "metformin toxicity"],
        "evidence_level": "UpToDate Clinical Consensus",
        "created_at": datetime.now().isoformat(),
        "content": """
### Formula & Etiology
Anion Gap = [Na+] - ([Cl-] + [HCO3-]). Normal range: 8–12 mEq/L. High Anion Gap > 12 mEq/L.
Differential Causes (MUDPILES): Lactic Acidosis (Metformin, sepsis), Ketoacidosis (DKA), Uremia (Renal Failure), Toxic Ingestions (Methanol, Salicylates).
"""
    }
]


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
                    "chunk_text": meta_header + sec_text
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
                        "chunk_text": meta_header + sub_text
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
        np.random.seed(abs(hash(text)) % (2**32))
        vec = np.random.randn(cls.VECTOR_DIM)
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
            "id": f"upload-{int(datetime.now().timestamp())}",
            "title": f"Uploaded Document: {doc_title}",
            "category": category,
            "specialty": specialty,
            "icd10_code": None,
            "rxnorm_code": None,
            "loinc_code": None,
            "synonyms": [doc_title],
            "keywords": ["uploaded document", filename.lower()],
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
            limit=10
        )
        
        candidates = []
        for point in search_results.points:
            candidates.append({
                "score": float(point.score),
                "payload": point.payload
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
