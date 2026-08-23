import logging
import re
from typing import Dict, Any, List
from app.modules.medical_agent.context.state import MedicalAgentState
from app.modules.medical_agent.agent.logging_utils import log_node_start, log_node_end
from app.modules.medical_agent.tools.rag_tools import tool_vector_rag_search

def _parse_disease_rag_content(chunk: Dict[str, Any]) -> Dict[str, Any]:
    """Parses structured disease overview, diagnostic criteria, and staging from RAG chunk content."""
    content = chunk.get("parent_content") or chunk.get("chunk_snippet") or chunk.get("content") or ""
    
    # Extract Overview / Pathophysiology
    overview = ""
    if "### Definisi & Patofisiologi" in content:
        overview = content.split("### Definisi & Patofisiologi")[1].split("###")[0].strip()
    elif "### Clinical Definition & Overview" in content:
        overview = content.split("### Clinical Definition & Overview")[1].split("###")[0].strip()
    elif "### Definisi Klinis" in content:
        overview = content.split("### Definisi Klinis")[1].split("###")[0].strip()
    elif "### Patofisiologi" in content:
        overview = content.split("### Patofisiologi")[1].split("###")[0].strip()
    elif "### Spektrum Klinis" in content:
        overview = content.split("### Spektrum Klinis")[1].split("###")[0].strip()
    else:
        overview = content[:350].strip()

    # Extract Diagnostic Criteria
    criteria = []
    for marker in ["### Kriteria Diagnosis Baku", "### Kriteria Diagnosis & Evaluasi", "### Diagnostic Criteria", "### Kriteria Diagnostik"]:
        if marker in content:
            crit_block = content.split(marker)[1].split("###")[0].strip()
            lines = [
                re.sub(r"^[0-9]+[\.\)]\s*", "", line.strip().lstrip("-* "))
                for line in crit_block.split("\n")
                if len(line.strip()) > 5
            ]
            criteria = lines[:4]
            break

    if not criteria:
        criteria = [
            "Evaluasi kriteria klinis terstandarisasi berbasis pedoman praktik klinis.",
            "Pemeriksaan laboratorium dan biomarker serial relevan.",
            "Pemeriksaan penunjang baku emas (Gold Standard) sesuai spesialisasi."
        ]

    # Extract Clinical Staging
    staging = ""
    for marker in ["### Tahapan & Stadium Klinis", "### Staging & Definition", "### Clinical Staging", "### Diagnostic Classification"]:
        if marker in content:
            stage_block = content.split(marker)[1].split("###")[0].strip()
            lines = [l.strip().lstrip("-* ") for l in stage_block.split("\n") if l.strip()]
            if lines:
                staging = lines[0]
            break

    if not staging:
        staging = f"Stadium Klinis Berbasis Panduan Praktik Klinis ({chunk.get('specialty', 'Internal Medicine')})"

    # Extract Key Complications
    complications = []
    for marker in ["### Komplikasi Klinis Utama", "### Key Complications & Risks", "### Komplikasi", "### Boxed Warning"]:
        if marker in content:
            comp_block = content.split(marker)[1].split("###")[0].strip()
            lines = [
                re.sub(r"^[0-9]+[\.\)]\s*", "", line.strip().lstrip("-* "))
                for line in comp_block.split("\n")
                if len(line.strip()) > 5
            ]
            complications = lines[:4]
            break

    if not complications:
        complications = [
            "Progresi keparahan penyakit kronis",
            "Risiko komplikasi mikrovaskular / makrovaskular bila target terapi tidak tercapai",
            "Penyakit penyerta atau disfungsi organ target"
        ]

    return {
        "disease_name": chunk.get("title", "Clinical Pathology Overview"),
        "disease_overview": overview,
        "diagnostic_criteria": criteria,
        "clinical_staging": staging,
        "key_complications": complications,
        "specialty": chunk.get("specialty", "Internal Medicine"),
        "evidence_level": chunk.get("evidence_level", "Evidence-Based Clinical Practice Guidelines"),
        "icd10_code": chunk.get("icd10_code"),
        "rag_score": chunk.get("reranked_score", chunk.get("score", 0.85))
    }

def node_km_disease_explanations(state: MedicalAgentState) -> MedicalAgentState:
    """Retrieves validated pathophysiological overviews, diagnostic criteria, and clinical staging dynamically from Qdrant Vector RAG."""
    log_node_start("km_disease_explanations", state, icon="📖")
    steps = list(state.get("steps_executed", []))
    anamnesis = state.get("simrs_anamnesis") or {}
    diag_rec = state.get("diagnostic_recommendations") or {}
    
    chief = (anamnesis.get("chief_complaint") or "").lower()
    rps = (anamnesis.get("history_present_illness") or "").lower()
    rpd = (anamnesis.get("past_medical_history") or "").lower()
    primary_diag_names = " ".join([p.get("diagnosis", "") for p in diag_rec.get("primary_recommendations", [])])
    
    # Step 1: Formulate clinical query for Qdrant Vector RAG search
    rag_query = f"{primary_diag_names} {chief} {rps} {rpd}".strip()

    # Step 2: Query Qdrant Vector RAG Store if query is present
    rag_chunks = tool_vector_rag_search(rag_query, top_k=4, category_filter="disease") if rag_query else []
    if not rag_chunks and rag_query:
        rag_chunks = tool_vector_rag_search(rag_query, top_k=4)

    # Step 3: Prioritize disease category chunks
    disease_chunks = [c for c in rag_chunks if c.get("category") == "disease"]
    primary_chunk = disease_chunks[0] if disease_chunks else (rag_chunks[0] if rag_chunks else None)

    if primary_chunk:
        explanation = _parse_disease_rag_content(primary_chunk)
        explanation["rag_source_chunks"] = rag_chunks
        steps.append({
            "step_name": "7. Penjelasan Patofisiologi Penyakit Pasien",
            "description": f"Mengambil ringkasan patofisiologi dan kriteria diagnosis dari basis pengetahuan vektor Qdrant RAG: {explanation.get('disease_name')}.",
            "status": "success",
            "result": {
                "disease_name": explanation.get("disease_name"),
                "clinical_staging": explanation.get("clinical_staging"),
                "evidence_level": explanation.get("evidence_level"),
                "diagnostic_criteria": explanation.get("diagnostic_criteria"),
                "key_complications": explanation.get("key_complications"),
                "rag_score": explanation.get("rag_score")
            }
        })
        log_node_end("km_disease_explanations", f"Disease: {explanation.get('disease_name')} | Staging: {explanation.get('clinical_staging')} | RAG Score: {explanation.get('rag_score')}")
    else:
        # Jika tidak ada query atau tidak ditemukan hasil yang relevan di RAG, kosongkan saja
        explanation = None
        steps.append({
            "step_name": "7. Penjelasan Patofisiologi Penyakit Pasien",
            "description": "Tidak ada data patofisiologi penyakit yang ditemukan di basis pengetahuan RAG untuk kueri/pasien ini.",
            "status": "info",
            "result": None
        })
        log_node_end("km_disease_explanations", "Tidak ada hasil RAG yang ditemukan (dikosongkan).")

    # Maintain rag_chunks in state for downstream LLM synthesis
    existing_rag = list(state.get("rag_chunks", []) or [])
    for rc in rag_chunks:
        if not any(e.get("title") == rc.get("title") for e in existing_rag):
            existing_rag.append(rc)

    return {
        **state,
        "steps_executed": steps,
        "disease_explanations": explanation,
        "rag_chunks": existing_rag
    }
