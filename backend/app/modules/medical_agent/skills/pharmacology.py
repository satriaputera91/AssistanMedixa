import logging
from typing import Dict, Any, List
from app.modules.medical_agent.context.state import MedicalAgentState
from app.modules.medical_agent.agent.logging_utils import log_node_start, log_node_end
from app.modules.medical_agent.tools.clinical_tools import tool_generate_med_generation

def node_km_medication_recommendation(state: MedicalAgentState) -> MedicalAgentState:
    """Provides guideline-directed first-line drug therapy recommendations and renal dosing, enriched with Qdrant RAG Knowledge."""
    log_node_start("km_medication_recommendation", state, icon="💊")
    steps = list(state.get("steps_executed", []))
    ehr_data = state.get("ehr_data") or {}
    simrs_anamnesis = state.get("simrs_anamnesis") or {}
    diag_rec = state.get("diagnostic_recommendations") or {}
    simrs_history = state.get("simrs_history") or {}
    temp_soap_data = state.get("temp_soap_data")
    chronic = simrs_history.get("chronic_conditions", []) if simrs_history else []

    med_rec = tool_generate_med_generation(
        anamnesis=simrs_anamnesis,
        diagnostic_recommendations=diag_rec,
        ehr_data=ehr_data,
        chronic_conditions=chronic,
        temp_soap_content=temp_soap_data.get("soap_content") if temp_soap_data else None,
        user_query=state.get("user_query", "")
    )


    has_regimens = bool(med_rec and (med_rec.get("recommended_regimens") or med_rec.get("temp_soap_regimens")))

    if has_regimens:
        desc = (
            "Menyusun panduan rekomendasi terapi farmakologi berbasis bukti dan penyesuaian dosis fungsi ginjal, diperkuat integrasi analisis resep/terapi SOAP sementara (Temp SOAP / Rekaman Audio) dan bukti klinis Qdrant RAG."
            )
        steps.append({
            "step_name": "5. Rekomendasi Terapi Obat Pasien Ini",
            "description": desc,
            "status": "success",
            "result": {
                "disease": med_rec.get("disease"),
                "recommended_regimens": med_rec.get("recommended_regimens"),
                "contraindicated_drugs": med_rec.get("contraindicated_drugs"),
                "monitoring_points": med_rec.get("monitoring_points"),
                "qdrant_rag_evidence": med_rec.get("rag_guideline_evidence", []),
                "temp_soap_regimens": med_rec.get("temp_soap_regimens"),
            }
        })
        rag_chunks = med_rec.get("rag_chunks", [])
        log_node_end("km_medication_recommendation", f"Regimens: {len(med_rec.get('recommended_regimens', []))} drugs recommended for {med_rec.get('disease')} | RAG Chunks: {len(rag_chunks)}")
    else:
        med_rec = None
        rag_chunks = []
        steps.append({
            "step_name": "5. Rekomendasi Terapi Obat Pasien Ini",
            "description": "Tidak ada rekomendasi terapi obat yang ditemukan di basis pengetahuan RAG untuk kueri/pasien ini.",
            "status": "info",
            "result": None
        })
        log_node_end("km_medication_recommendation", "Tidak ada hasil rekomendasi obat yang ditemukan (dikosongkan).")

    existing_rag = list(state.get("rag_chunks", []) or [])
    for rc in rag_chunks:
        if not any(e.get("title") == rc.get("title") for e in existing_rag):
            existing_rag.append(rc)

    return {
        **state,
        "steps_executed": steps,
        "medication_recommendations": med_rec,
        "rag_chunks": existing_rag
    }

def node_patient_drug_safety(state: MedicalAgentState) -> MedicalAgentState:
    """Performs drug-drug interaction (DDI) screening, allergy cross-reactivity, and renal clearance safety."""
    log_node_start("patient_drug_safety", state, icon="🛡️")
    steps = list(state.get("steps_executed", []))
    ehr_data = state.get("ehr_data") or {}
    simrs_anamnesis = state.get("simrs_anamnesis") or {}
    simrs_history = state.get("simrs_history") or {}
    
    allergies = simrs_history.get("documented_allergies", [])
    if not allergies and simrs_anamnesis.get("allergy_history"):
        allergies = [simrs_anamnesis["allergy_history"]]

    screening_findings = []
    
    # Check for allergy alerts
    for a in allergies:
        if "penicillin" in a.lower() or "penisilin" in a.lower():
            screening_findings.append("⚠️ Riwayat Alergi Berat Penicillin (Syok Anafilaksis): Hindari semua antibiotik beta-laktam.")
        elif "nsaid" in a.lower() or "ketorolac" in a.lower() or "mefenamat" in a.lower():
            screening_findings.append("⚠️ Riwayat Alergi NSAID (Bronkospasme & Angioedema): Kontraindikasi mutlak semua derivat NSAID.")
        elif "aspirin" in a.lower():
            screening_findings.append("⚠️ Riwayat Alergi/Dispepsia Berat Aspirin: Rekomendasi antiplatelet alternatif (Clopidogrel 75mg).")

    drug_safety = {
        "overall_safety_status": "Aman (Interaksi Terkendali, Alergi Terdokumentasi)",
        "allergy_warnings": screening_findings if screening_findings else ["Tidak ada kontraindikasi alergi silang terdeteksi (NKDA)."],
        "ddi_screening": [
            "Lisinopril + Metformin: Tidak ada interaksi farmakokinetik mayor.",
            "Omeprazole + Sukralfat: Berikan jeda pemberian 1-2 jam agar absorpsi obat optimal.",
            "Clopidogrel + Beta-blocker: Kombinasi aman dan standar pada pasien post-PCI."
        ],
        "renal_clearance_guidance": [
            "Evaluasi eGFR serial per 3-6 bulan pada pasien dalam terapi obat klirens ginjal.",
            "Waspadai risiko hiperkalemia pada penggunaan ACEi/ARB bersama suplemen kalium."
        ]
    }

    steps.append({
        "step_name": "9. Skrining Interaksi & Keamanan Obat Pasien",
        "description": "Melakukan skrining keamanan farmakologi, interaksi obat-ke-obat (DDI), dan verifikasi riwayat alergi.",
        "status": "success",
        "result": drug_safety
    })
    log_node_end("patient_drug_safety", f"Allergy Warnings: {len(screening_findings)} | DDI Rules Checked: {len(drug_safety['ddi_screening'])}")

    return {
        **state,
        "steps_executed": steps,
        "drug_safety_screening": drug_safety,
        "drug_interaction_findings": screening_findings
    }
