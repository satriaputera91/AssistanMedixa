import logging
from typing import Dict, Any, Optional
from app.modules.medical_agent.context.state import MedicalAgentState
from app.modules.medical_agent.tools.simrs_tools import tool_simrs_get_patient_labs
from app.modules.medical_agent.tools.clinical_tools import tool_generate_diagnostic_recommendations

logger = logging.getLogger("medical_agent.skills.diagnostics")

def node_eval_simrs_labs(state: MedicalAgentState) -> MedicalAgentState:
    """Evaluates serial laboratory panels, eGFR, uACR, and vital signs from SIMRS MCP."""
    patient_id = state.get("patient_id")
    steps = list(state.get("steps_executed", []))
    
    simrs_labs = None
    simrs_mrn = f"MRN-SIMRS-{patient_id.replace('P-', '')}" if (patient_id and patient_id.strip()) else None

    if simrs_mrn:
        labs_res = tool_simrs_get_patient_labs(simrs_mrn)
        if labs_res.get("status") == "success":
            simrs_labs = labs_res
            steps.append({
                "step_name": "3. Evaluasi Hasil Lab & Pemeriksaan SIMRS (MCP)",
                "description": f"Mengambil data laboratorium serial, nilai eGFR, dan tanda vital via MCP untuk {simrs_mrn}",
                "status": "success",
                "result": {
                    "tanda_vital": simrs_labs.get("vital_signs", {}),
                    "lab_serial": [f"{l['test_name']}: {l['value']} {l['unit']} ({l['status']})" for l in simrs_labs.get("latest_labs", [])]
                }
            })
        else:
            steps.append({
                "step_name": "3. Evaluasi Hasil Lab & Pemeriksaan SIMRS (MCP)",
                "description": f"Data laboratorium untuk {simrs_mrn} tidak ditemukan di SIMRS.",
                "status": "info",
                "result": "Hasil lab tidak tersedia."
            })
    else:
        steps.append({
            "step_name": "Evaluasi Hasil Lab SIMRS (Konsultasi Umum)",
            "description": "Tidak ada data pasien yang dipilih untuk evaluasi laboratorium spesifik.",
            "status": "info",
            "result": "Melewati evaluasi lab spesifik pasien."
        })

    return {
        **state,
        "steps_executed": steps,
        "simrs_lab_evaluations": simrs_labs
    }

def node_diagnostic_recommendation(state: MedicalAgentState) -> MedicalAgentState:
    """Generates primary & differential diagnoses with ICD-10 codification and confidence scoring."""
    steps = list(state.get("steps_executed", []))
    anamnesis = state.get("simrs_anamnesis")
    ehr_data = state.get("ehr_data")
    simrs_history = state.get("simrs_history")
    chronic = simrs_history.get("chronic_conditions", []) if simrs_history else []

    diag_rec = tool_generate_diagnostic_recommendations(
        anamnesis=anamnesis,
        ehr_data=ehr_data,
        chronic_conditions=chronic
    )

    steps.append({
        "step_name": "4. Rekomendasi Diagnosis & ICD-10 Pasien",
        "description": "Menghasilkan rekomendasi diagnosis kerja (primer) dan diagnosis banding lengkap dengan kodefikasi ICD-10.",
        "status": "success",
        "result": {
            "diagnosis_primer": diag_rec.get("primary_recommendations", []),
            "diagnosis_banding": diag_rec.get("differential_diagnoses", []),
            "kode_icd10": diag_rec.get("icd10_coding", []),
            "rencana_penunjang": diag_rec.get("recommended_workups", [])
        }
    })

    return {
        **state,
        "steps_executed": steps,
        "diagnostic_recommendations": diag_rec
    }
