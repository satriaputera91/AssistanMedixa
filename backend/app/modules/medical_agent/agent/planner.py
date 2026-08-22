import logging
from typing import Dict, Any, Optional
from app.modules.medical_agent.context.state import MedicalAgentState
from app.core.database import db

logger = logging.getLogger("medical_agent.agent.planner")

def _debug_node_start(node_name: str, state: MedicalAgentState, icon: str = "▶️"):
    patient_id = state.get("patient_id") or "N/A"
    patient_name = None
    if patient_id and patient_id != "N/A":
        try:
            p_rec = db.patient_records.get(patient_id)
            if p_rec:
                patient_name = p_rec.get("name")
        except Exception:
            pass
    pat_str = f"{patient_id} ({patient_name})" if patient_name else patient_id
    logger.info(f"{icon} [LANGGRAPH NODE START] >>> {node_name} | Patient: {pat_str} | Query: '{state.get('user_query', '')[:60]}'")

def _debug_node_end(node_name: str, message: str, icon: str = "✅"):
    logger.info(f"{icon} [LANGGRAPH NODE COMPLETED] <<< {node_name} | {message}")

def _debug_edge(source: str, target: str, condition: str = ""):
    cond_str = f" (Condition: {condition})" if condition else ""
    logger.info(f"🔀 [LANGGRAPH EDGE TRANSITION] {source} ──▶ {target}{cond_str}")

def node_planner(state: MedicalAgentState) -> MedicalAgentState:
    """Classifies clinical queries, determines intents, and plans workflow execution paths."""
    _debug_node_start("planner", state, icon="🧠")
    query = state.get("user_query", "")
    query_lower = query.lower()
    patient_id = state.get("patient_id")
    steps = list(state.get("steps_executed", []))
    
    # 1. GENERAL MEDICAL KNOWLEDGE CONSULTATION (No active patient selected)
    is_general_knowledge_mode = not patient_id or not patient_id.strip()

    if is_general_knowledge_mode:
        if any(k in query_lower for k in ["pedoman", "guideline", "kriteria diagnosis", "staging", "kriteria diagnostik", "konsensus"]):
            detected_intent = "1. Pedoman Klinis & Kriteria Diagnosis (Knowledge Management)"
        elif any(k in query_lower for k in ["panduan terapi", "lini pertama", "rejimen", "terapi obat", "pemilihan obat", "first-line"]):
            detected_intent = "2. Panduan Terapi & Rejimen Lini Pertama (Knowledge Management)"
        elif any(k in query_lower for k in ["panduan tindakan", "prosedur medis", "protokol tindakan", "indikasi tindakan"]):
            detected_intent = "3. Panduan Tindakan & Prosedur Medis (Clinical Guidelines)"
        elif any(k in query_lower for k in ["penyesuaian dosis", "renal dosing", "hepatic", "gangguan ginjal", "penurunan egfr", "fungsi hati"]):
            detected_intent = "4. Penyesuaian Dosis Ginjal & Hepar (Knowledge Management)"
        elif any(k in query_lower for k in ["skrining interaksi", "interaksi obat", "ddi", "kombinasi berisiko", "kontraindikasi"]):
            detected_intent = "5. Skrining Interaksi Obat & Kontraindikasi (Knowledge Management)"
        elif any(k in query_lower for k in ["tanda bahaya", "red flag", "ambang kritis", "kegawatdaruratan", "kriteria rujukan"]):
            detected_intent = "6. Deteksi Tanda Bahaya & Kedaruratan (Knowledge Management)"
        elif any(k in query_lower for k in ["biomarker", "hasil lab", "interpretasi lab", "nilai normal", "nilai rujukan"]):
            detected_intent = "7. Interpretasi Biomarker & Hasil Lab (Knowledge Management)"
        elif any(k in query_lower for k in ["patofisiologi", "mekanisme penyakit", "etiologi"]):
            detected_intent = "8. Penjelasan Patofisiologi & Mekanisme Penyakit (Knowledge Management)"
        else:
            detected_intent = None

        if detected_intent:
            steps.append({
                "step_name": "Agent Intelligence & Knowledge Planner",
                "description": f"Knowledge Intent: '{detected_intent}' (Konsultasi Medis Umum)",
                "status": "completed",
                "result": {"detected_intent": detected_intent, "mode": "general_consultation"}
            })
            _debug_node_end("planner", f"Intent: '{detected_intent}' | Mode: General Consultation (Knowledge Management)")
        else:
            steps.append({
                "step_name": "Agent Intelligence & Conversation Handler",
                "description": "Merespons kueri konsultasi umum melalui basis pengetahuan medis (Knowledge Management).",
                "status": "completed",
                "result": {"detected_intent": None, "mode": "general_consultation"}
            })
            _debug_node_end("planner", "Intent: None (General consultation / knowledge)")

        return {
            **state,
            "detected_intent": detected_intent,
            "steps_executed": steps
        }

    # 2. PATIENT-SPECIFIC CLINICAL CONSULTATION (Connected with SIMRS)
    if any(k in query_lower for k in ["buat cppt", "kirim cppt", "kirim soap", "buat soap", "sinkronisasi cppt", "simpan cppt", "kirim/sinkronisasikan", "update simrs", "sync simrs", "commit emr", "kirim ke simrs", "kirim/sinkronisasi"]):
        detected_intent = "10. Buat & Kirim CPPT S/O/A/P ke SIMRS (MCP)"
    elif any(k in query_lower for k in ["ambil informasi riwayat", "ambil data profil", "profil demografi", "riwayat penyakit kronis", "rawat inap", "riwayat pasien", "informasi riwayat", "catatan perkembangan", "riwayat catatan", "s/o/a/p", "soap terakhir", "progress note", "admission"]):
        detected_intent = "1. Ambil Informasi Riwayat Pasien (SIMRS MCP)"
    elif any(k in query_lower for k in ["anamnesis", "keluhan", "rps", "rpd", "rpk", "tinjauan sistem"]):
        detected_intent = "2. Ambil Data Anamnesis SIMRS (MCP)"
    elif any(k in query_lower for k in ["riwayat", "demografi"]):
        detected_intent = "1. Ambil Informasi Riwayat Pasien (SIMRS MCP)"
    elif any(k in query_lower for k in ["lab", "laboratorium", "ttv", "tanda vital", "egfr", "uacr", "hba1c", "elektrolit", "tensi"]):
        detected_intent = "3. Evaluasi Hasil Lab & Pemeriksaan SIMRS (MCP)"
    elif any(k in query_lower for k in ["diagnosis", "icd", "banding", "differential"]):
        detected_intent = "4. Rekomendasi Diagnosis & ICD-10"
    elif any(k in query_lower for k in ["rekomendasi obat", "terapi obat", "dosis", "regimen", "peresepan"]):
        detected_intent = "5. Rekomendasi Terapi Obat Berbasis Bukti (Knowledge Management)"
    elif any(k in query_lower for k in ["rekomendasi tindakan", "prosedur medis", "rencana tindakan", "tindakan medis", "intervensi klinis", "tindakan", "prosedur"]):
        detected_intent = "6. Rekomendasi Tindakan & Prosedur Medis (Clinical Procedures & Interventions)"
    elif any(k in query_lower for k in ["patofisiologi", "penjelasan penyakit", "kriteria diagnostik", "staging"]):
        detected_intent = "7. Penjelasan Penyakit & Patofisiologi (Knowledge Management)"
    elif any(k in query_lower for k in ["tanda bahaya", "red flag", "bahaya", "urgensi", "kegawatdaruratan"]):
        detected_intent = "8. Deteksi Tanda Bahaya & Red Flags (Knowledge Management)"
    elif any(k in query_lower for k in ["skrining", "interaksi obat", "keamanan obat", "ddi", "efek samping"]):
        detected_intent = "9. Skrining Interaksi & Keamanan Obat Pasien"
    elif any(k in query_lower for k in ["evaluasi klinis", "evaluasi lengkap", "laporan lengkap", "semua data", "evaluasi terpadu", "ringkasan lengkap", "konsultasi lengkap", "seluruh pemeriksaan"]):
        detected_intent = "Evaluasi Klinis Terpadu SIMRS & Knowledge Management"
    else:
        detected_intent = None

    simrs_mrn = f"MRN-SIMRS-{patient_id.replace('P-', '')}"
    
    patient_name = None
    try:
        p_rec = db.patient_records.get(patient_id)
        if p_rec:
            patient_name = p_rec.get("name")
    except Exception:
        pass
    pat_str = f"{patient_id} ({patient_name})" if patient_name else patient_id
    
    if detected_intent:
        steps.append({
            "step_name": "Agent Intelligence & Clinical Planner",
            "description": f"Clinical Intent Detected: '{detected_intent}' (Target Patient: {pat_str}, MRN: {simrs_mrn})",
            "status": "completed",
            "result": {"detected_intent": detected_intent, "simrs_mrn": simrs_mrn, "patient_name": patient_name}
        })
        _debug_node_end("planner", f"Intent: '{detected_intent}' | Patient: {pat_str} | MRN: {simrs_mrn}")
    else:
        steps.append({
            "step_name": "Agent Intelligence & Conversation Handler",
            "description": f"Tidak ada intent klinis khusus yang terdeteksi ({pat_str}). Merespons kueri secara percakapan langsung.",
            "status": "completed",
            "result": {"detected_intent": None, "patient_name": patient_name}
        })
        _debug_node_end("planner", f"Intent: None (Direct conversation) | Patient: {pat_str}")

    return {
        **state,
        "detected_intent": detected_intent,
        "steps_executed": steps
    }
