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
from app.core.database import dbApplication

def node_fetch_patient_history(state: MedicalAgentState) -> MedicalAgentState:
    """Retrieves patient demographics, chronic history, and admissions from SIMRS, as well as temp SOAP if present."""
    log_node_start("fetch_patient_history", state, icon="👤")
    patient_id = state.get("patient_id")
    steps = list(state.get("steps_executed", []))
    
    ehr_result = None
    simrs_profile = None
    simrs_history = None
    temp_soap_data = None

    simrs_mrn = f"MRN-SIMRS-{patient_id.replace('P-', '')}" if (patient_id and patient_id.strip()) else None

    if simrs_mrn:
        # Step 2A: Query SIMRS Demographics & Profile via MCP
        simrs_prof_res = tool_simrs_get_patient_profile(simrs_mrn)
        if simrs_prof_res.get("status") == "success":
            simrs_profile = simrs_prof_res["profile"]
            steps.append({
                "step_name": "1. Ambil Informasi Demografi Pasien (SIMRS MCP)",
                "description": f"Mengambil data identitas, demografi, NIK, dan BPJS pasien melalui Model Context Protocol ({simrs_mrn})",
                "status": "success",
                "result": {
                    "mrn": simrs_profile.get("mrn"),
                    "nama_lengkap": simrs_profile.get("full_name"),
                    "nik": simrs_profile.get("nik"),
                    "usia": simrs_profile.get("age"),
                    "jenis_kelamin": simrs_profile.get("gender"),
                    "golongan_darah": simrs_profile.get("blood_type"),
                    "no_bpjs": simrs_profile.get("bpjs_card_no"),
                    "kelas_bpjs": simrs_profile.get("bpjs_class"),
                    "poliklinik": simrs_profile.get("active_clinic"),
                    "dpjp": simrs_profile.get("attending_physician")
                }
            })
        else:
            steps.append({
                "step_name": "1. Ambil Informasi Demografi Pasien (SIMRS MCP)",
                "description": f"Mencari profil demografi pasien di SIMRS ({simrs_mrn})",
                "status": "info",
                "result": f"Data profil demografi untuk {simrs_mrn} tidak ditemukan di SIMRS."
            })
            
        # Optional: Query history for downstream nodes if needed
        simrs_hist_res = tool_simrs_get_patient_history(simrs_mrn)
        if simrs_hist_res.get("status") == "success":
            simrs_history = simrs_hist_res["history"]

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

        # Step 2D: Check Temp SOAP records in Application Database (e.g. from Audio Recording / Consultation Draft)
        if patient_id:
            temp_list = dbApplication.list_temp_soap(patient_id=patient_id, limit=1)
            if temp_list:
                temp_soap_data = temp_list[0]
                sc = temp_soap_data.get("soap_content") or {}
                steps.append({
                    "step_name": "Sinkronisasi SOAP Temp & Rekaman Konsultasi",
                    "description": f"Ditemukan data SOAP sementara aktif ({temp_soap_data.get('temp_id')}) untuk integrasi analisis klinis komprehensif",
                    "status": "success",
                    "result": {
                        "temp_id": temp_soap_data.get("temp_id"),
                        "status": temp_soap_data.get("status"),
                        "audio_filename": temp_soap_data.get("audio_filename"),
                        "keluhan_terkini": sc.get("subjective", "-")[:80],
                        "asesmen_sementara": sc.get("assessment", "-")[:80],
                        "rencana_terapi": sc.get("plan", "-")[:80]
                    }
                })

        log_node_end("fetch_patient_history", f"SIMRS Profile: {bool(simrs_profile)} | History: {bool(simrs_history)} | Temp SOAP: {bool(temp_soap_data)}")
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
        "simrs_history": simrs_history,
        "temp_soap_data": temp_soap_data
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
                "step_name": "2. Ambil Anamnesis Sebelumnya (MCP)",
                "description": f"MengAmbil Anamnesis Sebelumnya klinis lengkap dari modul RME SIMRS untuk {simrs_mrn}",
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
                "step_name": "2. Ambil Anamnesis Sebelumnya (MCP)",
                "description": f"Data anamnesis untuk {simrs_mrn} belum tercatat di SIMRS.",
                "status": "info",
                "result": f"Data anamnesis untuk {simrs_mrn} tidak ditemukan di SIMRS."
            })
            log_node_end("fetch_patient_anamnesis", "Anamnesis data not found in SIMRS")
    else:
        steps.append({
            "step_name": "Ambil Anamnesis Sebelumnya (Konsultasi Umum)",
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
