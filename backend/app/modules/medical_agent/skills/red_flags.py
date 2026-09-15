import logging
from typing import Dict, Any, List
from app.modules.medical_agent.context.state import MedicalAgentState
from app.modules.medical_agent.logging_utils import log_node_start, log_node_end
from app.modules.medical_agent.tools.clinical_tools import tool_detect_clinical_red_flags

def node_km_red_flag_detection(state: MedicalAgentState) -> MedicalAgentState:
    """Identifies clinical red flags, emergency thresholds, and vital sign anomalies dynamically retrieved from Qdrant Vector RAG."""
    log_node_start("km_red_flag_detection", state, icon="🚨")
    steps = list(state.get("steps_executed", []))
    simrs_anamnesis = state.get("simrs_anamnesis") or {}
    simrs_labs = state.get("simrs_lab_evaluations") or {}
    diag_rec = state.get("diagnostic_recommendations") or {}
    ehr_data = state.get("ehr_data") or {}

    red_flags_res = tool_detect_clinical_red_flags(
        anamnesis=simrs_anamnesis,
        diagnostic_recommendations=diag_rec,
        labs=simrs_labs,
        ehr_data=ehr_data,
        user_query=state.get("user_query", "")
    )

    detected_flags = red_flags_res.get("detected_red_flags", [])
    rag_chunks = red_flags_res.get("rag_chunks", [])

    if detected_flags:
        steps.append({
            "step_name": "8. Deteksi Tanda Bahaya & Red Flags Pasien",
            "description": "Melakukan evaluasi klinis ambang kedaruratan, deteksi tanda bahaya (red flags), dan panduan triase darurat berbasis bukti Qdrant RAG.",
            "status": "success",
            "result": red_flags_res
        })
        log_node_end("km_red_flag_detection", f"Detected {len(detected_flags)} red flags alerts ({', '.join([f.get('severity', 'High') for f in detected_flags])})")
    else:
        red_flags_res = None
        steps.append({
            "step_name": "8. Deteksi Tanda Bahaya & Red Flags Pasien",
            "description": "Tidak ada indikasi tanda bahaya (red flags) spesifik yang terdeteksi dari basis pengetahuan RAG untuk kondisi pasien saat ini.",
            "status": "info",
            "result": None
        })
        log_node_end("km_red_flag_detection", "Tidak ada tanda bahaya (red flags) yang terdeteksi (dikosongkan).")

    # Maintain rag_chunks in state for downstream LLM synthesis
    existing_rag = list(state.get("rag_chunks", []) or [])
    for rc in rag_chunks:
        if not any(e.get("title") == rc.get("title") for e in existing_rag):
            existing_rag.append(rc)

    return {
        **state,
        "steps_executed": steps,
        "red_flag_detections": red_flags_res,
        "rag_chunks": existing_rag
    }
