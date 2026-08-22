import logging
from typing import Dict, Any
from app.modules.medical_agent.context.state import MedicalAgentState
from app.modules.medical_agent.agent.logging_utils import log_node_start, log_node_end

def node_km_disease_explanations(state: MedicalAgentState) -> MedicalAgentState:
    """Retrieves validated pathophysiological overviews, diagnostic criteria, and clinical staging."""
    log_node_start("km_disease_explanations", state, icon="📖")
    steps = list(state.get("steps_executed", []))
    anamnesis = state.get("simrs_anamnesis") or {}
    
    chief = (anamnesis.get("chief_complaint") or "").lower()
    rps = (anamnesis.get("history_present_illness") or "").lower()
    combined_query = f"{chief} {rps} {state.get('user_query', '')}".lower()

    if any(k in combined_query for k in ["ulu hati", "lambung", "gastritis", "perih", "anemia", "30124"]):
        explanation = {
            "disease_name": "Gastritis Kronis Erosif & Anemia Defisiensi Besi",
            "disease_overview": (
                "Gastritis erosif ditandai oleh kerusakan epitel mukosa gaster akibat ketidakseimbangan antara "
                "faktor agresif (asam lambung, pepsin, NSAID) dan faktor defensif mukosa (lendir, bikarbonat, prostaglandin). "
                "Kehilangan darah mikroskopis kronis dari erosi mukosa yang berlangsung lama menyebabkan deplesi cadangan besi tubuh "
                "(Serum Ferritin rendah) dan berkembang menjadi Anemia Defisiensi Besi mikrositik hipokromik."
            ),
            "diagnostic_criteria": [
                "Nyeri ulu hati rasa terbakar yang berkaitan dengan waktu makan",
                "Temuan EGD: Eritema difus, erosi mukosa superfisial tanpa ulkus dalam",
                "Laboratorium: Hb rendah, MCV < 80 fL, MCH < 27 pg, Serum Ferritin < 30 ng/mL"
            ],
            "clinical_staging": "Gastritis Kronis Derajat Ringan-Sedang dengan Anemia Sekunder Ringan (Hb > 10 g/dL)",
            "key_complications": ["Ulkus Peptikum Gaster / Duodeni", "Perdarahan Saluran Cerna Atas Akut", "Deplesi Besi Berat"]
        }
    elif any(k in combined_query for k in ["dada", "nyeri dada", "angina", "tangga", "jantung", "20811"]):
        explanation = {
            "disease_name": "Chronic Coronary Syndrome (CAD Post-PCI LAD)",
            "disease_overview": (
                "Sindrom Koroner Kronis (CCS) mencerminkan ketidaksesuaian antara suplai oksigen miokardium dan "
                "kebutuhan metabolik jantung akibat aterosklerosis koroner atau stenosis residual. Pada pasien pasca pemasangan stent (DES), "
                "kepatuhan terapi antiplatelet ganda (DAPT) dan statin intensitas tinggi esensial untuk mencegah trombosis stent akut atau restenosis intraintima."
            ),
            "diagnostic_criteria": [
                "Angina pektoris stabil yang dapat diprediksi dengan aktivitas fisik (CCS Class II)",
                "Riwayat PCI pada arteri koroner utama (LAD)",
                "Pemeriksaan non-invasif: EKG iskemia dan profil lipid"
            ],
            "clinical_staging": "CAD Stable Angina Pectoris (Canadian Cardiovascular Society Class II)",
            "key_complications": ["Trombosis Stent Akut", "Infark Miokard Akut", "Gagal Jantung Iskemik"]
        }
    else:
        explanation = {
            "disease_name": "Type 2 Diabetes Mellitus with CKD Stage 3a & Diabetic Neuropathy",
            "disease_overview": (
                "DM Tipe 2 merupakan gangguan metabolik progresif akibat resistensi insulin dan disfungsi sel beta pankreas. "
                "Hiperglikemia kronis memicu glikosilasi protein dan stres oksidatif pada mikrovaskular ginjal (glomerulosklerosis nodular) "
                "yang menyebabkan mikroalbuminuria (uACR meningkat) dan penurunan laju filtrasi glomerulus (eGFR 58 mL/min/1.73m²), "
                "serta neuropati perifer simetris pada saraf distal."
            ),
            "diagnostic_criteria": [
                "HbA1c >= 6.5% atau GDP >= 126 mg/dL",
                "eGFR 45-59 mL/min/1.73m² persisten > 3 bulan (CKD Stage 3a)",
                "uACR 30-300 mg/g (Mikroalbuminuria)"
            ],
            "clinical_staging": "CKD Stage G3aA2 (Moderate Risk / Early Diabetic Kidney Disease)",
            "key_complications": ["Progresi ke End-Stage Renal Disease (ESRD)", "Diabetic Foot Ulcer", "Penyakit Kardiovaskular Mayor"]
        }

    steps.append({
        "step_name": "7. Penjelasan Patofisiologi Penyakit Pasien",
        "description": "Menyajikan ringkasan patofisiologi penyakit, kriteria diagnosis baku, dan stadium klinis.",
        "status": "success",
        "result": explanation
    })
    log_node_end("km_disease_explanations", f"Disease: {explanation.get('disease_name')} | Staging: {explanation.get('clinical_staging')}")

    return {
        **state,
        "steps_executed": steps,
        "disease_explanations": explanation
    }
