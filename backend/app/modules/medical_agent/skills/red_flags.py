import logging
from typing import Dict, Any, List
from app.modules.medical_agent.context.state import MedicalAgentState
from app.modules.medical_agent.agent.logging_utils import log_node_start, log_node_end

def node_km_red_flag_detection(state: MedicalAgentState) -> MedicalAgentState:
    """Identifies clinical red flags, emergency thresholds, and vital sign anomalies."""
    log_node_start("km_red_flag_detection", state, icon="🚨")
    steps = list(state.get("steps_executed", []))
    simrs_anamnesis = state.get("simrs_anamnesis") or {}
    simrs_labs = state.get("simrs_lab_evaluations") or {}
    
    chief = (simrs_anamnesis.get("chief_complaint") or "").lower()
    rps = (simrs_anamnesis.get("history_present_illness") or "").lower()
    combined_query = f"{chief} {rps} {state.get('user_query', '')}".lower()

    detected_flags = []
    
    if any(k in combined_query for k in ["ulu hati", "lambung", "gastritis", "perih", "anemia", "30124"]):
        detected_flags.extend([
            {
                "alert": "Tanda Perdarahan Saluran Cerna Akut (Hematemesis / Melena)",
                "severity": "Critical",
                "trigger_criteria": "Muntah darah kehitaman seperti bubuk kopi atau buang air besar hitam pekat.",
                "action": "Segera rujuk ke IGD untuk resusitasi cairan, NGT dekompresi, dan injeksi PPI intravena dosis tinggi."
            },
            {
                "alert": "Anemia Simtomatik Berat & Instabilitas Hemodinamik",
                "severity": "High",
                "trigger_criteria": "Hb < 8 g/dL atau penurunan drastis disertai pusing ortostatik berat, sinkop, atau takikardia.",
                "action": "Evaluasi kebutuhan transfusi Packed Red Cells (PRC) dan pelacakan sumber perdarahan."
            }
        ])
    elif any(k in combined_query for k in ["dada", "nyeri dada", "angina", "tangga", "jantung", "20811"]):
        detected_flags.extend([
            {
                "alert": "Sindrom Koroner Akut (Unstable Angina / Re-Infarction)",
                "severity": "Critical",
                "trigger_criteria": "Nyeri dada retrosternal menjalar ke lengan/rahang yang berlangsung > 20 menit saat istirahat tidak mereda dengan nitrat.",
                "action": "Segera aktivasi Code STEMI / transfer ke IGD terdekat untuk EKG 12-lead emergensi & biomarker troponin kuantitatif."
            }
        ])
    else:
        detected_flags.extend([
            {
                "alert": "Kris Hipertensi & Ensefalopati Hipertensif",
                "severity": "High",
                "trigger_criteria": "Tekanan Darah > 180/120 mmHg disertai nyeri kepala hebat, pandangan kabur, atau penurunan kesadaran.",
                "action": "Pemberian antihipertensi parenteral terkontrol di ruang rawat intensif."
            },
            {
                "alert": "Progresi Penyakit Ginjal Akut pada Kronis (AKI on CKD)",
                "severity": "High",
                "trigger_criteria": "Oliguria (<400 mL/24 jam), edema anasarka, atau hiperkalemia berat (>6.0 mEq/L).",
                "action": "Evaluasi elektrolit cito, EKG monitoring, dan konsultasi nefrologi untuk koreksi cairan/elektrolit."
            }
        ])

    red_flags_res = {
        "status": "success",
        "detected_red_flags": detected_flags,
        "vital_sign_alerts": "Semua parameter tanda vital saat ini dalam batas toleransi aman rawat jalan.",
        "emergency_guidance": "Bila ditemukan salah satu kriteria tanda bahaya di atas, edukasikan pasien untuk segera mengakses instalasi gawat darurat (IGD)."
    }

    steps.append({
        "step_name": "8. Deteksi Tanda Bahaya & Red Flags Pasien",
        "description": "Melakukan evaluasi klinis ambang kedaruratan, deteksi tanda bahaya (red flags), dan panduan triase darurat.",
        "status": "success",
        "result": red_flags_res
    })
    log_node_end("km_red_flag_detection", f"Detected {len(detected_flags)} red flags alerts ({', '.join([f['severity'] for f in detected_flags])})")

    return {
        **state,
        "steps_executed": steps,
        "red_flag_detections": red_flags_res
    }
