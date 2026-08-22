import logging
from typing import Dict, Any, Optional
from app.modules.medical_agent.context.state import MedicalAgentState
from app.modules.medical_agent.tools.simrs_tools import (
    tool_simrs_get_patient_profile,
    tool_simrs_get_patient_history,
    tool_simrs_get_patient_anamnesis
)
from app.modules.medical_agent.tools.clinical_tools import tool_query_patient_ehr
from app.modules.medical_agent.agent.logging_utils import log_node_start, log_node_end

def node_fetch_patient_history(state: MedicalAgentState) -> MedicalAgentState:
    """Retrieves patient demographics, chronic history, and admissions from SIMRS."""
    log_node_start("fetch_patient_history", state, icon="👤")
    patient_id = state.get("patient_id")
    steps = list(state.get("steps_executed", []))
    
    ehr_result = None
    simrs_profile = None
    simrs_history = None

    simrs_mrn = f"MRN-SIMRS-{patient_id.replace('P-', '')}" if (patient_id and patient_id.strip()) else None

    if simrs_mrn:
        # Step 2A: Query SIMRS Demographics & Profile via MCP
        simrs_prof_res = tool_simrs_get_patient_profile(simrs_mrn)
        if simrs_prof_res.get("status") == "success":
            simrs_profile = simrs_prof_res["profile"]
            steps.append({
                "step_name": "Ambil Profil & Demografi Pasien SIMRS (MCP)",
                "description": f"Mengambil data demografi, NIK, dan BPJS pasien melalui Model Context Protocol ({simrs_mrn})",
                "status": "success",
                "result": f"Nama: {simrs_profile['full_name']} | NIK: {simrs_profile['nik']} | BPJS: {simrs_profile['bpjs_card_no']} ({simrs_profile['bpjs_class']})"
            })
        else:
            steps.append({
                "step_name": "Ambil Profil & Demografi Pasien SIMRS (MCP)",
                "description": f"Mencari profil pasien di SIMRS ({simrs_mrn})",
                "status": "info",
                "result": f"Data profil demografi untuk {simrs_mrn} tidak ditemukan di SIMRS."
            })
            
        # Step 2B: Query SIMRS Chronic Conditions, Past Admissions & SOAP Notes via MCP
        simrs_hist_res = tool_simrs_get_patient_history(simrs_mrn)
        if simrs_hist_res.get("status") == "success":
            simrs_history = simrs_hist_res["history"]
            soap_note = simrs_history.get("last_soap_progress_note", {})
            steps.append({
                "step_name": "1. Ambil Informasi Riwayat Pasien (SIMRS MCP)",
                "description": f"Mengambil riwayat penyakit kronis, riwayat rawat inap, catatan alergi, dan riwayat klinis dari basis data SIMRS",
                "status": "success",
                "result": {
                    "penyakit_kronis": simrs_history.get("chronic_conditions", []),
                    "riwayat_rawat_inap": simrs_history.get("past_admissions", []),
                    "catatan_perkembangan_soap": soap_note
                }
            })
        else:
            steps.append({
                "step_name": "1. Ambil Informasi Riwayat Pasien (SIMRS MCP)",
                "description": f"Mencari riwayat penyakit kronis dan rawat inap di SIMRS ({simrs_mrn})",
                "status": "info",
                "result": f"Data riwayat penyakit kronis & rawat inap untuk {simrs_mrn} tidak ditemukan di SIMRS."
            })

        # Step 2C: Query Local EHR Database (Diagnoses, Allergies, Medications, Labs)
        if patient_id:
            ehr_res = tool_query_patient_ehr(patient_id)
            if ehr_res.get("status") == "success":
                ehr_result = ehr_res["data"]
                steps.append({
                    "step_name": "Sinkronisasi Rekam Medis EHR Pasien",
                    "description": f"Mengambil rekam medis lengkap (Diagnosis, Alergi, Terapi Obat, Hasil Lab) untuk pasien {patient_id}",
                    "status": "success",
                    "result": {
                        "nama": ehr_result.get("name"),
                        "diagnosa": ehr_result.get("diagnoses", []),
                        "alergi": ehr_result.get("allergies", []),
                        "obat_aktif": [m["name"] for m in ehr_result.get("current_medications", [])],
                        "lab_terbaru": ehr_result.get("recent_labs", {})
                    }
                })
        log_node_end("fetch_patient_history", f"SIMRS Profile: {bool(simrs_profile)} | History: {bool(simrs_history)} | EHR: {bool(ehr_result)}")
    else:
        steps.append({
            "step_name": "Konsultasi Medis Umum (Tanpa Data Pasien)",
            "description": "Tidak ada data pasien yang dipilih untuk sesi konsultasi medis umum.",
            "status": "info",
            "result": "Melewati pengambilan data rekam medis pasien."
        })
        log_node_end("fetch_patient_history", "Skipped (General Consultation Mode)")

    return {
        **state,
        "steps_executed": steps,
        "ehr_data": ehr_result,
        "simrs_profile": simrs_profile,
        "simrs_history": simrs_history
    }

def node_fetch_patient_anamnesis(state: MedicalAgentState) -> MedicalAgentState:
    """Retrieves patient clinical anamnesis (Chief Complaint, RPS, RPD, RPK) from SIMRS MCP."""
    log_node_start("fetch_patient_anamnesis", state, icon="📝")
    patient_id = state.get("patient_id")
    steps = list(state.get("steps_executed", []))
    
    simrs_anamnesis = None
    simrs_mrn = f"MRN-SIMRS-{patient_id.replace('P-', '')}" if (patient_id and patient_id.strip()) else None

    if simrs_mrn:
        anamnesis_res = tool_simrs_get_patient_anamnesis(simrs_mrn)
        if anamnesis_res.get("status") == "success":
            simrs_anamnesis = anamnesis_res["anamnesis"]
            steps.append({
                "step_name": "2. Ambil Data Anamnesis SIMRS (MCP)",
                "description": f"Mengambil data anamnesis klinis lengkap dari modul RME SIMRS untuk {simrs_mrn}",
                "status": "success",
                "result": {
                    "keluhan_utama": simrs_anamnesis.get("chief_complaint"),
                    "riwayat_penyakit_sekarang": simrs_anamnesis.get("history_present_illness"),
                    "riwayat_penyakit_dahulu": simrs_anamnesis.get("past_medical_history"),
                    "riwayat_pengobatan": simrs_anamnesis.get("medication_history"),
                    "riwayat_alergi": simrs_anamnesis.get("allergy_history")
                }
            })
            log_node_end("fetch_patient_anamnesis", f"Chief Complaint: '{simrs_anamnesis.get('chief_complaint')}'")
        else:
            steps.append({
                "step_name": "2. Ambil Data Anamnesis SIMRS (MCP)",
                "description": f"Data anamnesis untuk {simrs_mrn} belum tercatat di SIMRS.",
                "status": "info",
                "result": f"Data anamnesis untuk {simrs_mrn} tidak ditemukan di SIMRS."
            })
            log_node_end("fetch_patient_anamnesis", "Anamnesis data not found in SIMRS")
    else:
        steps.append({
            "step_name": "Ambil Data Anamnesis SIMRS (Konsultasi Umum)",
            "description": "Tidak ada data pasien yang dipilih.",
            "status": "info",
            "result": "Melewati pengambilan anamnesis pasien."
        })
        log_node_end("fetch_patient_anamnesis", "Skipped (General Consultation Mode)")

    return {
        **state,
        "steps_executed": steps,
        "simrs_anamnesis": simrs_anamnesis
    }
