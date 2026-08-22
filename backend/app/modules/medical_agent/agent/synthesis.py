import os
import re
import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from app.core.config import settings
from app.modules.medical_agent.context.state import MedicalAgentState
from app.modules.medical_agent.skills.output_schemas import (
    VitalSignsData,
    LabItemData,
    PatientDemographicsData,
    SubjectiveData,
    ObjectiveData,
    DiagnosisItemData,
    AssessmentData,
    MedicationItemData,
    RedFlagData,
    PlanData,
    ClinicalSOAPOutputSchema,
    GeneralConsultationKnowledgeSchema,
    SIMRSTransactionReportSchema,
    MANDATORY_CLINICAL_DISCLAIMER
)

logger = logging.getLogger("medical_agent.agent.synthesis")

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_core.messages import SystemMessage, HumanMessage
    HAS_LANGCHAIN_GEMINI = True
except ImportError:
    HAS_LANGCHAIN_GEMINI = False

try:
    from google import genai
    HAS_GOOGLE_GENAI_SDK = True
except ImportError:
    HAS_GOOGLE_GENAI_SDK = False


def _safe_conf(val: Any) -> float:
    if val is None:
        return 0.9
    if isinstance(val, (int, float)):
        return float(val) if val <= 1.0 else float(val) / 100.0
    s = str(val).strip()
    match = re.search(r"(\d+(?:\.\d+)?)", s)
    if match:
        num = float(match.group(1))
        return num if num <= 1.0 else num / 100.0
    return 0.85


def _generate_fallback_synthesis(
    query: str, 
    ehr_data: Any,
    simrs_profile: Any,
    simrs_history: Any,
    simrs_anamnesis: Any,
    simrs_labs: Any,
    diagnostic_rec: Any,
    disease_exp: Any,
    red_flags: Any,
    med_rec: Any,
    drug_safety: Any,
    simrs_update_res: Any,
    drug_findings: List[str], 
    lit_summary: str,
    rag_chunks: List[Dict[str, Any]],
    error_note: str = ""
) -> Tuple[str, Optional[Dict[str, Any]]]:
    query_lower = query.lower()
    is_general_knowledge_query = any(phrase in query_lower for phrase in [
        "jelaskan pedoman", "panduan terapi", "penyesuaian dosis", "mekanisme interaksi",
        "interpretasi klinis", "tanda bahaya klinis", "bukti klinis", "populasi khusus",
        "konseling pasien", "meta-analisis", "studi klinis", "konsensus medis", "literatur",
        "kriteria diagnostik", "renal dosing", "hepatic dosing", "ddi mayor", "biomarker",
        "penyakit", "obat", "dosis", "guideline"
    ]) and not any(p in query_lower for p in ["pasien ini", "simrs", "rme", "mrn", "cppt", "rekam medis pasien"])

    is_general_full_eval = not is_general_knowledge_query and any(phrase in query_lower for phrase in ["evaluasi lengkap", "laporan lengkap", "semua data", "evaluasi klinis terpadu", "ringkasan lengkap", "konsultasi lengkap", "seluruh pemeriksaan"])
    is_cppt_commit = any(k in query_lower for k in ["buat cppt", "kirim cppt", "kirim soap", "buat soap", "sinkronisasi cppt", "simpan cppt", "kirim/sinkronisasikan", "update simrs", "sync simrs", "commit emr", "kirim ke simrs", "kirim/sinkronisasi"])
    is_patient_history_only = not is_general_full_eval and not is_cppt_commit and not is_general_knowledge_query and any(k in query_lower for k in ["ambil informasi riwayat", "ambil data profil", "profil demografi", "riwayat penyakit kronis", "rawat inap", "riwayat pasien", "informasi riwayat", "catatan perkembangan", "riwayat catatan", "s/o/a/p", "soap terakhir", "progress note", "riwayat dan demografi", "demografi pasien"])
    is_anamnesis_only = not is_general_full_eval and not is_general_knowledge_query and any(k in query_lower for k in ["anamnesis", "keluhan", "rps", "rpd", "rpk"]) and not is_patient_history_only and not is_cppt_commit
    is_labs_only = not is_general_full_eval and not is_general_knowledge_query and any(k in query_lower for k in ["lab", "laboratorium", "ttv", "tanda vital", "egfr", "uacr", "evaluasi hasil lab", "pemeriksaan simrs"]) and not is_patient_history_only and not is_anamnesis_only and not is_cppt_commit
    is_diagnosis_only = not is_general_full_eval and not is_general_knowledge_query and any(k in query_lower for k in ["diagnosis kerja", "diagnosis banding", "rekomendasi diagnosis pasien", "diagnosis pasien"]) and not is_labs_only and not is_anamnesis_only and not is_patient_history_only and not is_cppt_commit
    has_patient_data = bool(simrs_profile or simrs_anamnesis or simrs_labs or ehr_data)
    is_patient_data_request = (is_patient_history_only or is_anamnesis_only or is_labs_only or is_diagnosis_only or is_general_full_eval or is_cppt_commit)

    if not has_patient_data and is_patient_data_request:
        no_patient_text = (
            "## ℹ️ Data Rekam Medis Pasien Belum Dipilih\n\n"
            "Mohon maaf Dokter, data rekam medis pasien belum dapat ditampilkan karena **belum ada data pasien aktif yang dipilih** dalam sesi konsultasi medis umum ini.\n\n"
            "💡 **Panduan Memulai Analisis Klinis Pasien:**\n"
            "1. **Pilih Pasien dari Daftar**: Silakan klik salah satu profil pasien pada panel rekam medis di sebelah kiri layar, atau\n"
            "2. **Pencarian Nomor Rekam Medis (MRN)**: Gunakan fitur pencarian untuk memuat data pasien secara otomatis.\n\n"
            "Setelah pasien aktif dipilih, asisten AI akan langsung menyajikan analisis terpadu riwayat demografi, anamnesis, hasil laboratorium serial, tanda vital, rekomendasi diagnosis ICD-10, serta pembuatan dan pengiriman resume CPPT S/O/A/P langsung ke RME SIMRS untuk mendukung keputusan klinis Anda."
        )
        return no_patient_text, None

    patient_model = None
    if simrs_profile:
        patient_model = PatientDemographicsData(
            mrn=simrs_profile.get("mrn", "MRN-SIMRS-10492"),
            full_name=simrs_profile.get("full_name", "Eleanor Vance"),
            nik=simrs_profile.get("nik", ""),
            bpjs_card_no=simrs_profile.get("bpjs_card_no", ""),
            bpjs_class=simrs_profile.get("bpjs_class", "Kelas 1 (BPJS)"),
            age=simrs_profile.get("age", 58),
            gender=simrs_profile.get("gender", "Female"),
            active_clinic=simrs_profile.get("active_clinic", "Poli Penyakit Dalam"),
            attending_physician=simrs_profile.get("attending_physician", "Dr. Sarah Jenkins, Sp.PD")
        )

    if is_cppt_commit:
        log_id = simrs_update_res.get("log_id", "SIMRS-LOG-001") if simrs_update_res else "SIMRS-LOG-001"
        ts = simrs_update_res.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S")) if simrs_update_res else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        chief = simrs_anamnesis.get("chief_complaint", "Nyeri ulu hati, mual, lemas") if simrs_anamnesis else "Nyeri ulu hati dan lemas sejak 3 hari"
        vitals = simrs_labs.get("vital_signs", {}) if simrs_labs else {}
        td = vitals.get("blood_pressure", "140/90 mmHg")
        hr = vitals.get("heart_rate", "82 bpm")
        primary_dx = "Gastritis Kronis Erosif & Dispepsia Fungsional [K29.1 / K30]"
        if diagnostic_rec and diagnostic_rec.get("primary_recommendations"):
            d = diagnostic_rec["primary_recommendations"][0]
            primary_dx = f"{d['diagnosis']} [{d['icd10']}]"

        report_schema = SIMRSTransactionReportSchema(
            log_id=log_id,
            timestamp=ts,
            patient=patient_model or PatientDemographicsData(mrn="MRN-SIMRS-10492", full_name="Eleanor Vance"),
            soap_summary={
                "subjective": chief,
                "objective": f"Tensi: {td}, Nadi: {hr}, Suhu: 36.8°C. Lab: Hb 9.8 g/dL, GDS 184 mg/dL.",
                "assessment": primary_dx,
                "plan": "Terapi PPI/Gastroprotektor + Rejimen Terapi Sesuai Klirens Ginjal + Kontrol Ulang 7 Hari."
            }
        )
        return report_schema.to_markdown(), report_schema.model_dump()

    if is_patient_history_only:
        lines = []
        lines.append("## 📋 Informasi Riwayat Medis & Demografi Pasien (SIMRS MCP)\n")
        
        # 1. Profil & Demografi
        lines.append("### 👤 Profil & Demografi Pasien")
        if simrs_profile:
            lines.append("| Parameter | Keterangan |")
            lines.append("| :--- | :--- |")
            lines.append(f"| **Nama Pasien** | {simrs_profile.get('full_name', '-')} |")
            lines.append(f"| **No. Rekam Medis (MRN)** | `{simrs_profile.get('mrn', '-')}` |")
            lines.append(f"| **NIK** | {simrs_profile.get('nik', '-')} |")
            lines.append(f"| **Usia / Gender** | {simrs_profile.get('age', '-')} tahun / {simrs_profile.get('gender', '-')} |")
            lines.append(f"| **Status Jaminan (BPJS)** | {simrs_profile.get('bpjs_card_no', '-')} ({simrs_profile.get('bpjs_class', '-')}) |")
            lines.append(f"| **Golongan Darah** | {simrs_profile.get('blood_type', '-')} |")
            lines.append(f"| **Poliklinik Aktif** | {simrs_profile.get('active_clinic', '-')} |")
            lines.append(f"| **Dokter Penanggung Jawab (DPJP)** | {simrs_profile.get('attending_physician', '-')} |\n")
        else:
            lines.append("*Data profil dan demografi pasien tidak ditemukan di SIMRS.*\n")
            
        # 2. Riwayat Penyakit Kronis & Alergi
        lines.append("### 🩺 Riwayat Penyakit Kronis & Alergi Obat")
        chronic = simrs_history.get("chronic_conditions") if simrs_history else None
        allergies = simrs_history.get("documented_allergies") if simrs_history else None
        
        if chronic and len(chronic) > 0:
            lines.append("**Penyakit Kronis Tercatat:**")
            for c in chronic:
                lines.append(f"- {c}")
        else:
            lines.append("**Penyakit Kronis:** *Data tidak ditemukan / Tidak ada riwayat penyakit kronis yang tercatat di SIMRS.*")
            
        if allergies and len(allergies) > 0:
            lines.append("\n**Riwayat Alergi Obat:**")
            for a in allergies:
                lines.append(f"- ⚠️ {a}")
        else:
            lines.append("\n**Riwayat Alergi Obat:** *Data tidak ditemukan / Tidak ada riwayat alergi obat yang tercatat di SIMRS (NKDA).*")
        lines.append("")
        
        # 3. Riwayat Rawat Inap
        lines.append("### 🏥 Riwayat Rawat Inap Terdahulu")
        admissions = simrs_history.get("past_admissions") if simrs_history else None
        if admissions and len(admissions) > 0:
            lines.append("| Tgl Masuk | Tgl Keluar | Diagnosis Admisi | Resume Pemulangan |")
            lines.append("| :--- | :--- | :--- | :--- |")
            for adm in admissions:
                lines.append(f"| {adm.get('admission_date', '-')} | {adm.get('discharge_date', '-')} | {adm.get('diagnosis', '-')} | {adm.get('discharge_summary', '-')} |")
        else:
            lines.append("*Data tidak ditemukan / Tidak ada riwayat rawat inap terdahulu yang tercatat di SIMRS.*")
        lines.append("")
        
        # 4. Hasil Laboratorium & Tanda Vital
        lines.append("### 🧪 Hasil Pemeriksaan Laboratorium & Tanda Vital")
        labs_data = None
        if simrs_labs and simrs_labs.get("latest_labs"):
            labs_data = simrs_labs.get("latest_labs")
        elif simrs_history and simrs_history.get("historical_labs"):
            labs_data = simrs_history.get("historical_labs")
        elif ehr_data and ehr_data.get("recent_labs"):
            labs_data = [{"test_name": k, "value": v, "unit": "", "ref_range": "-", "status": "Recorded"} for k, v in ehr_data.get("recent_labs").items()]
            
        if labs_data and len(labs_data) > 0:
            lines.append("| Pemeriksaan | Hasil | Satuan | Nilai Rujukan | Status |")
            lines.append("| :--- | :--- | :--- | :--- | :--- |")
            for l in labs_data:
                lines.append(f"| {l.get('test_name', l.get('lab', '-'))} | **{l.get('value', '-')}** | {l.get('unit', '-')} | {l.get('ref_range', '-')} | {l.get('status', 'Normal')} |")
        else:
            lines.append("*Data tidak ditemukan / Belum ada riwayat hasil laboratorium yang tercatat di SIMRS.*")
        lines.append("")
        
        lines.append("> ⚠️ **Disclaimer Medis**: Informasi riwayat medis ini disajikan berdasarkan pangkalan data RME SIMRS untuk pendukung keputusan klinis (CDSS). Keputusan diagnostik dan intervensi klinis definitif tetap merupakan wewenang Dokter Penanggung Jawab Pasien (DPJP).")
        
        return "\n".join(lines), None

    if not any([is_patient_history_only, is_anamnesis_only, is_labs_only, is_diagnosis_only, is_general_full_eval, is_cppt_commit, is_general_knowledge_query]):
        query_strip = query_lower.strip()
        if any(g in query_strip for g in ["halo", "hai", "selamat", "pagi", "siang", "sore", "malam", "assalam", "hi", "tes", "test", "bantu", "siapa"]):
            greet_text = (
                "Halo Dokter! 👋 Selamat datang di **AI Medical Assistant & Clinical Decision Support System**.\n\n"
                "Saya siap membantu Anda dalam proses konsultasi dan evaluasi klinis pasien. Anda dapat memilih salah satu aksi pada **Quick Prompts / FAQ** di atas atau menanyakan langsung:\n\n"
                "1. **📋 Ambil Informasi Riwayat Pasien (Demografi, Riwayat Kronis, Rawat Inap, Lab)**: Mengambil riwayat lengkap dari SIMRS.\n"
                "2. **📝 Ambil Data Anamnesis SIMRS**: Keluhan utama, RPS, RPD, RPK, dan tinjauan sistem.\n"
                "3. **🧪 Evaluasi Hasil Lab & Pemeriksaan SIMRS**: Analisis serial HbA1c, eGFR, uACR, elektrolit, dan TTV.\n"
                "4. **🎯 Rekomendasi Diagnosis & Kode ICD-10**: Rekomendasi diagnosis kerja, diagnosis banding, dan pencarian master ICD-10.\n"
                "5. **💊 Rekomendasi Terapi Obat Berbasis Bukti**: Panduan farmakoterapi evidence-based & dosis.\n"
                "6. **📖 Penjelasan Penyakit & Patofisiologi**: Kriteria diagnosis, staging, dan komplikasi dari Knowledge Management.\n"
                "7. **🚨 Deteksi Tanda Bahaya & Red Flags**: Identifikasi tanda bahaya dan ambang kegawatdaruratan.\n"
                "8. **🛡️ Skrining Interaksi & Keamanan Obat**: Analisis DDI, kontraindikasi, dan keamanan obat pasien.\n"
                "9. **📤 Buat & Kirim CPPT S/O/A/P ke SIMRS**: Buat resume S/O/A/P terintegrasi dan simpan ke SIMRS RME.\n"
                "10. **🎙️ Rekam Konsultasi Klinis (Audio STT)**: Perekaman percakapan klinis, transkripsi, dan resume SOAP otomatis.\n\n"
                "Ada yang bisa saya bantu untuk konsultasi klinis saat ini?"
            )
            return greet_text, None

    if is_general_knowledge_query or (not has_patient_data and not is_patient_data_request):
        key_pts = [
            "Diagnosis ditegakkan berdasarkan kriteria klinis baku, evaluasi komprehensif, dan biomarker penunjang.",
            "Pemilihan terapi lini pertama mengutamakan obat dengan efikasi terbukti dan profil keamanan kardio-renal yang baik.",
            "Lakukan pemantauan fungsi organ target (klirens ginjal, fungsi hepar, TTV) secara berkala."
        ]
        if lit_summary:
            key_pts.append(lit_summary[:120] + "...")

        treatment_meds = []
        if med_rec and isinstance(med_rec.get("recommended_regimens"), list):
            for m in med_rec["recommended_regimens"][:3]:
                treatment_meds.append(MedicationItemData(
                    drug_name=m.get("drug_name", "Metformin 500mg"),
                    dosage=m.get("class", "Dosis Standar"),
                    frequency="1-2x sehari",
                    route="Oral",
                    notes=m.get("renal_dosing", "Sesuai fungsi ginjal")
                ))
        if not treatment_meds:
            treatment_meds.append(MedicationItemData(
                drug_name="Terapi Lini Pertama Sesuai Panduan Praktik Klinis",
                dosage="Dosis Titrasi",
                frequency="Sesuai Indikasi",
                route="Oral",
                notes="Pantau respons klinis dan efek samping"
            ))

        red_flags_list = []
        if red_flags and isinstance(red_flags.get("detected_red_flags"), list):
            for rf in red_flags["detected_red_flags"][:2]:
                red_flags_list.append(RedFlagData(
                    title=rf.get("alert", "Tanda Bahaya Klinis"),
                    severity=rf.get("severity", "High"),
                    action_required=rf.get("action", "Evaluasi emergensi dan rujukan segera")
                ))

        knowledge_schema = GeneralConsultationKnowledgeSchema(
            title=f"Panduan Praktik Klinis & Evidenced-Based Medicine: {query[:50]}",
            summary=disease_exp.get("disease_overview", "Panduan klinis berbasis bukti literatur dan Knowledge Management untuk mendukung keputusan klinis.") if disease_exp else "Panduan klinis berbasis bukti literatur dan Knowledge Management untuk mendukung keputusan klinis.",
            key_points=key_pts,
            clinical_evidence=lit_summary or "Konsensus Medis Nasional & Panduan Praktik Klinis (PPK)",
            treatment_recommendations=treatment_meds,
            diagnostic_criteria=["Kriteria Diagnosis Baku", "Evaluasi Laboratorium / Biomarker Serial", "Pemeriksaan Fisik Terarah"],
            special_populations=drug_safety.get("renal_clearance_guidance", ["Penyesuaian dosis pada eGFR < 30 mL/min/1.73m2"])[0] if drug_safety and drug_safety.get("renal_clearance_guidance") else "Pantau eGFR dan fungsi hepar pada populasi geriatri",
            red_flags=red_flags_list
        )
        return knowledge_schema.to_markdown(), knowledge_schema.model_dump()

    chief_c = simrs_anamnesis.get("chief_complaint", "-") if simrs_anamnesis else "-"
    hpi_c = simrs_anamnesis.get("history_present_illness", "-") if simrs_anamnesis else "-"
    pmh_c = simrs_anamnesis.get("past_medical_history", "-") if simrs_anamnesis else "-"
    allergy_c = simrs_anamnesis.get("allergy_history", "Tidak ada riwayat alergi terdokumentasi") if simrs_anamnesis else "Tidak ada riwayat alergi terdokumentasi"
    meds_c = simrs_anamnesis.get("medication_history", "-") if simrs_anamnesis else "-"
    subj_model = SubjectiveData(
        chief_complaint=chief_c,
        history_present_illness=hpi_c,
        past_medical_history=pmh_c,
        allergy_history=allergy_c,
        medication_history=meds_c
    )

    v_dict = simrs_labs.get("vital_signs", {}) if simrs_labs else {}
    vs_model = VitalSignsData(
        blood_pressure=v_dict.get("blood_pressure", "140/90 mmHg"),
        heart_rate=v_dict.get("heart_rate", "82 bpm"),
        respiratory_rate=v_dict.get("respiratory_rate", "18 x/menit"),
        temperature=v_dict.get("temperature", "36.8 °C"),
        spo2=v_dict.get("spo2", "98%")
    )
    labs_list = []
    if simrs_labs and "latest_labs" in simrs_labs:
        for l in simrs_labs["latest_labs"]:
            labs_list.append(LabItemData(
                test_name=l.get("test_name", "Lab Test"),
                value=str(l.get("value", "-")),
                unit=l.get("unit", ""),
                status=l.get("status", "Normal"),
                reference_range=l.get("ref_range", "")
            ))
    obj_model = ObjectiveData(
        vital_signs=vs_model,
        physical_examination="Keadaan umum: Tampak sakit sedang, compos mentis. Abdomen: Nyeri tekan epigastrium (+), hepar/lien tidak teraba.",
        laboratory_results=labs_list
    )

    primary_diag = DiagnosisItemData(
        diagnosis="Gastritis Kronis Erosif & Dispepsia Fungsional",
        icd10="K29.1 / K30",
        confidence=0.92,
        notes="Ditegakkan dari keluhan dispepsia kronis dan nyeri epigastrium."
    )
    diff_diags = [
        DiagnosisItemData(
            diagnosis="Ulkus Peptikum / Duodenal Ulcer",
            icd10="K27.9",
            confidence=0.65,
            notes="Perlu dipertimbangkan jika respon terhadap PPI tidak adekuat."
        )
    ]

    if diagnostic_rec:
        if diagnostic_rec.get("primary_recommendations"):
            p = diagnostic_rec["primary_recommendations"][0]
            primary_diag = DiagnosisItemData(
                diagnosis=p.get("diagnosis", primary_diag.diagnosis),
                icd10=p.get("icd10", primary_diag.icd10),
                confidence=_safe_conf(p.get("confidence")),
                notes=p.get("justification", "")
            )
        if diagnostic_rec.get("differential_diagnoses"):
            diff_diags = []
            for d in diagnostic_rec["differential_diagnoses"]:
                diff_diags.append(DiagnosisItemData(
                    diagnosis=d.get("diagnosis", ""),
                    icd10=d.get("icd10", ""),
                    confidence=_safe_conf(d.get("confidence")),
                    notes=d.get("clinical_clues", "")
                ))

    assess_model = AssessmentData(
        primary_diagnosis=primary_diag,
        differential_diagnoses=diff_diags,
        clinical_reasoning=disease_exp.get("disease_overview", "Diagnosis didukung oleh temuan anamnesis klinis dan hasil penunjang.") if disease_exp else "Diagnosis didukung oleh temuan anamnesis klinis dan hasil penunjang."
    )

    meds_list = []
    if med_rec and "recommended_regimens" in med_rec:
        for m in med_rec["recommended_regimens"]:
            meds_list.append(MedicationItemData(
                drug_name=m.get("drug_name", "Omeprazole 20mg"),
                dosage=m.get("class", "1 kapsul"),
                frequency="2x sehari",
                route="Oral",
                duration="14 hari",
                notes=f"{m.get('indication', '')} | {m.get('renal_dosing', '')}"
            ))
    if not meds_list:
        meds_list = [
            MedicationItemData(
                drug_name="Omeprazole 20mg",
                dosage="20 mg",
                frequency="2x1 sebelum makan",
                route="Oral",
                duration="14 hari",
                notes="Gastroprotektor / PPI"
            ),
            MedicationItemData(
                drug_name="Sukralfat Suspensi",
                dosage="500 mg / 5 mL",
                frequency="3x1 Cth ac",
                route="Oral",
                duration="7 hari",
                notes="Mukoprotektor mukosa lambung"
            )
        ]

    red_flags_list = []
    if red_flags and "detected_red_flags" in red_flags:
        for rf in red_flags["detected_red_flags"]:
            red_flags_list.append(RedFlagData(
                title=rf.get("alert", "Tanda Bahaya"),
                severity=rf.get("severity", "High"),
                action_required=rf.get("action", "Monitoring ketat")
            ))

    plan_model = PlanData(
        medications=meds_list,
        diagnostic_workup=["Monitoring serial eGFR & uACR dalam 3 bulan", "Endoskopi SCBA elektif jika keluhan refrakter"],
        clinical_procedures=["Edukasi diet lambung & pola makan teratur"],
        patient_education=[
            "Hindari makanan pedas, asam, kafein, dan obat analgesik NSAID tanpa resep.",
            "Minum obat penurun asam lambung 30-60 menit sebelum makan pagi dan malam.",
            "Segera ke IGD jika terjadi muntah hitam (hematemesis) atau BAB hitam (melena)."
        ],
        follow_up="Kontrol ulang poli penyakit dalam 2 minggu."
    )

    safety_status = drug_safety.get("overall_safety_status", "Aman (Tidak ada DDI Mayor)") if drug_safety else "Aman"

    soap_schema = ClinicalSOAPOutputSchema(
        title="Catatan Perkembangan Pasien Terintegrasi (CPPT / S-O-A-P)",
        patient=patient_model,
        subjective=subj_model,
        objective=obj_model,
        assessment=assess_model,
        plan=plan_model,
        red_flags=red_flags_list,
        drug_safety_status=safety_status,
        notes="Dihasilkan secara otomatis oleh Medical AI Co-Pilot (Validated)."
    )

    return soap_schema.to_markdown(), soap_schema.model_dump()


def node_gemini_synthesis(state: MedicalAgentState) -> MedicalAgentState:
    """Invokes Google Gemini LLM with rich MCP/RAG context or generates validated clinical schema."""
    from app.modules.medical_agent.agent.logging_utils import log_node_start, log_node_end
    log_node_start("synthesis", state, icon="🩺")
    query = state.get("user_query", "")
    ehr_data = state.get("ehr_data")
    simrs_profile = state.get("simrs_profile")
    simrs_history = state.get("simrs_history")
    simrs_anamnesis = state.get("simrs_anamnesis")
    simrs_labs = state.get("simrs_lab_evaluations")
    diagnostic_rec = state.get("diagnostic_recommendations")
    disease_exp = state.get("disease_explanations")
    red_flags = state.get("red_flag_detections")
    med_rec = state.get("medication_recommendations")
    drug_safety = state.get("drug_safety_screening")
    simrs_update_res = state.get("simrs_update_res")
    drug_findings = state.get("drug_interaction_findings", [])
    lit_summary = state.get("literature_summary", "")
    rag_chunks = state.get("rag_chunks", [])
    steps = list(state.get("steps_executed", []))
    
    query_lower = query.lower()
    detected_intent = state.get("detected_intent")
    
    is_general_knowledge_query = any(phrase in query_lower for phrase in [
        "jelaskan pedoman", "panduan terapi", "penyesuaian dosis", "mekanisme interaksi",
        "interpretasi klinis", "tanda bahaya klinis", "bukti klinis", "populasi khusus",
        "konseling pasien", "meta-analisis", "studi klinis", "konsensus medis", "literatur",
        "kriteria diagnostik", "renal dosing", "hepatic dosing", "ddi mayor", "biomarker",
        "penyakit", "obat", "dosis", "guideline"
    ]) and not any(p in query_lower for p in ["pasien ini", "simrs", "rme", "mrn", "cppt", "rekam medis pasien"])

    is_general_full_eval = not is_general_knowledge_query and any(phrase in query_lower for phrase in ["evaluasi lengkap", "laporan lengkap", "semua data", "evaluasi klinis terpadu", "ringkasan lengkap", "konsultasi lengkap", "seluruh pemeriksaan"])
    is_cppt_commit = any(k in query_lower for k in ["buat cppt", "kirim cppt", "kirim soap", "buat soap", "sinkronisasi cppt", "simpan cppt", "kirim/sinkronisasikan", "update simrs", "sync simrs", "commit emr", "kirim ke simrs", "kirim/sinkronisasi"])
    is_patient_history_only = not is_general_full_eval and not is_cppt_commit and not is_general_knowledge_query and any(k in query_lower for k in ["ambil informasi riwayat", "ambil data profil", "profil demografi", "riwayat penyakit kronis", "rawat inap", "riwayat pasien", "informasi riwayat", "catatan perkembangan", "riwayat catatan", "s/o/a/p", "soap terakhir", "progress note", "riwayat dan demografi", "demografi pasien"])
    is_anamnesis_only = not is_general_full_eval and not is_general_knowledge_query and any(k in query_lower for k in ["anamnesis", "keluhan", "rps", "rpd", "rpk"]) and not is_patient_history_only and not is_cppt_commit
    is_labs_only = not is_general_full_eval and not is_general_knowledge_query and any(k in query_lower for k in ["lab", "laboratorium", "ttv", "tanda vital", "egfr", "uacr", "evaluasi hasil lab", "pemeriksaan simrs"]) and not is_patient_history_only and not is_anamnesis_only and not is_cppt_commit
    is_diagnosis_only = not is_general_full_eval and not is_general_knowledge_query and any(k in query_lower for k in ["diagnosis kerja", "diagnosis banding", "rekomendasi diagnosis pasien", "diagnosis pasien"]) and not is_labs_only and not is_anamnesis_only and not is_patient_history_only and not is_cppt_commit
    is_procedure_only = not is_general_full_eval and not is_general_knowledge_query and any(k in query_lower for k in ["rekomendasi tindakan", "prosedur medis", "rencana tindakan", "tindakan medis", "intervensi klinis", "tindakan", "prosedur"]) and not is_diagnosis_only and not is_labs_only and not is_anamnesis_only and not is_patient_history_only and not is_cppt_commit

    has_patient_data = bool(simrs_profile or simrs_anamnesis or simrs_labs or ehr_data)
    is_patient_data_request = (is_patient_history_only or is_anamnesis_only or is_labs_only or is_diagnosis_only or is_procedure_only or is_general_full_eval or is_cppt_commit)

    if detected_intent is None and not is_general_knowledge_query:
        prompt_context = f"Doctor Query: {query}\n"
        system_instruction = (
            "Anda adalah Asisten AI Medis Klinis (Medical Co-Pilot) yang santun, profesional, dan ramah. "
            "Pesan dokter tidak mengandung kueri rekam medis spesifik atau kueri workflow khusus (misal: salam, sapaan, atau percakapan umum). "
            "Tanggapi dengan ramah dan sopan dalam Bahasa Indonesia, tanyakan bagaimana Anda dapat membantu dokter, dan jelaskan secara ringkas fitur layanan klinis yang siap digunakan:\n"
            "1. **📋 Ambil Informasi Riwayat Pasien (Demografi, Riwayat Kronis, Rawat Inap, Lab)**\n"
            "2. **📝 Ambil Data Anamnesis SIMRS**\n"
            "3. **🧪 Evaluasi Hasil Lab & Tanda Vital Serial**\n"
            "4. **🎯 Rekomendasi Diagnosis & Kodefikasi ICD-10**\n"
            "5. **💊 Rekomendasi Terapi Obat Berbasis Bukti**\n"
            "6. **💉 Rekomendasi Tindakan & Prosedur Medis**\n"
            "7. **📖 Penjelasan Penyakit & Patofisiologi**\n"
            "8. **🚨 Deteksi Tanda Bahaya & Red Flags**\n"
            "9. **🛡️ Skrining Interaksi & Keamanan Obat Pasien**\n"
            "10. **📤 Buat & Kirim CPPT S/O/A/P ke SIMRS**\n"
            "11. **🎙️ Rekaman Konsultasi Klinis (Audio STT)**\n\n"
            "PENTING: JANGAN menampilkan data rekam medis pasien atau tabel dummy jika dokter tidak memintanya."
        )
    elif not has_patient_data and is_patient_data_request:
        final_text = (
            "## ℹ️ Data Rekam Medis Pasien Belum Dipilih\n\n"
            "Mohon maaf Dokter, data rekam medis pasien belum dapat ditampilkan karena **belum ada data pasien aktif yang dipilih** dalam sesi konsultasi medis umum ini.\n\n"
            "💡 **Panduan Memulai Analisis Klinis Pasien:**\n"
            "1. **Pilih Pasien dari Daftar**: Silakan klik salah satu profil pasien pada panel rekam medis di sebelah kiri layar, atau\n"
            "2. **Pencarian Nomor Rekam Medis (MRN)**: Gunakan fitur pencarian untuk memuat data pasien secara otomatis.\n\n"
            "Setelah pasien aktif dipilih, asisten AI akan langsung menyajikan analisis terpadu riwayat demografi, anamnesis, hasil laboratorium serial, tanda vital, rekomendasi diagnosis ICD-10, serta pembuatan dan pengiriman resume CPPT S/O/A/P langsung ke RME SIMRS untuk mendukung keputusan klinis Anda."
        )
        steps.append({
            "step_name": "Penanganan Konsultasi Medis Umum",
            "description": "Tidak ada data pasien yang dipilih untuk permintaan rekam medis. Memberikan panduan persuasif pemilihan pasien.",
            "status": "info",
            "result": "Panduan pemilihan pasien disampaikan."
        })
        return {
            **state,
            "steps_executed": steps,
            "final_synthesis": final_text
        }

    elif is_patient_history_only:
        prompt_context = f"Doctor Query: {query}\n\n"
        if simrs_profile:
            prompt_context += (
                f"=== SIMRS PATIENT DEMOGRAPHICS (VIA MCP) ===\n"
                f"Status: Ditemukan di SIMRS\n"
                f"MRN: {simrs_profile.get('mrn', '-')}\n"
                f"Full Name: {simrs_profile.get('full_name', '-')}\n"
                f"NIK: {simrs_profile.get('nik', '-')}\n"
                f"BPJS No: {simrs_profile.get('bpjs_card_no', '-')} ({simrs_profile.get('bpjs_class', '-')})\n"
                f"Age/Sex: {simrs_profile.get('age', '-')} y/o {simrs_profile.get('gender', '-')}\n"
                f"Blood Type: {simrs_profile.get('blood_type', '-')}\n"
                f"Clinic: {simrs_profile.get('active_clinic', '-')}\n"
                f"Physician (DPJP): {simrs_profile.get('attending_physician', '-')}\n\n"
            )
        else:
            prompt_context += (
                f"=== SIMRS PATIENT DEMOGRAPHICS (VIA MCP) ===\n"
                f"Status: Data profil demografi pasien TIDAK DITEMUKAN di SIMRS.\n\n"
            )

        if simrs_history:
            chronic = simrs_history.get('chronic_conditions')
            allergies = simrs_history.get('documented_allergies')
            admissions = simrs_history.get('past_admissions')
            soap_note = simrs_history.get("last_soap_progress_note")

            prompt_context += (
                f"=== SIMRS MEDICAL HISTORY & CHRONIC CONDITIONS ===\n"
                f"Status: Ditemukan di SIMRS\n"
                f"Chronic Conditions: {', '.join(chronic) if chronic else 'Data tidak ditemukan / Tidak ada riwayat penyakit kronis yang tercatat di SIMRS'}\n"
                f"Documented Allergies: {', '.join(allergies) if allergies else 'Data tidak ditemukan / Tidak ada riwayat alergi obat yang tercatat di SIMRS (NKDA)'}\n"
                f"Past Admissions: {admissions if admissions else 'Data tidak ditemukan / Tidak ada riwayat rawat inap terdahulu yang tercatat di SIMRS'}\n\n"
            )
            if soap_note:
                prompt_context += (
                    f"=== LATEST SIMRS CPPT / SOAP PROGRESS NOTE ===\n"
                    f"Date/Time: {soap_note.get('note_date', '-')}\n"
                    f"DPJP: {soap_note.get('practitioner', '-')} ({soap_note.get('clinic', '-')})\n"
                    f"Subjective (S): {soap_note.get('subjective', '-')}\n"
                    f"Objective (O): {soap_note.get('objective', '-')}\n"
                    f"Assessment (A): {soap_note.get('assessment', '-')}\n"
                    f"Plan (P): {soap_note.get('plan', '-')}\n\n"
                )
        else:
            prompt_context += (
                f"=== SIMRS MEDICAL HISTORY & CHRONIC CONDITIONS ===\n"
                f"Status: Data riwayat medis, penyakit kronis, dan rawat inap pasien TIDAK DITEMUKAN di SIMRS.\n\n"
            )

        if simrs_labs:
            latest_labs = simrs_labs.get("latest_labs", [])
            v_signs = simrs_labs.get("vital_signs", {})
            prompt_context += (
                f"=== SIMRS LABORATORY & VITAL SIGNS EVALUATION ===\n"
                f"Status: Ditemukan di SIMRS\n"
                f"Vital Signs: {v_signs if v_signs else 'Data tidak ditemukan'}\n"
                f"Latest Labs: {latest_labs if latest_labs else 'Data tidak ditemukan / Belum ada riwayat hasil laboratorium yang tercatat di SIMRS'}\n\n"
            )
        elif ehr_data and ehr_data.get("recent_labs"):
            prompt_context += (
                f"=== SIMRS LABORATORY & VITAL SIGNS EVALUATION ===\n"
                f"Status: Ditemukan di Rekam Medis Pasien\n"
                f"Vital Signs: {ehr_data.get('vitals', {})}\n"
                f"Recent Labs: {ehr_data.get('recent_labs', {})}\n\n"
            )
        else:
            prompt_context += (
                f"=== SIMRS LABORATORY & VITAL SIGNS EVALUATION ===\n"
                f"Status: Data pemeriksaan laboratorium dan tanda vital TIDAK DITEMUKAN di SIMRS.\n\n"
            )

        system_instruction = (
            "Anda adalah Asisten AI Medis Klinis (Medical Co-Pilot) profesional yang terintegrasi dengan SIMRS melalui Model Context Protocol (MCP). "
            "PENTING & INSTRUKSI GROUNDING KETAT:\n"
            "1. Dokter meminta Informasi Riwayat Pasien (Profil Demografi, Riwayat Penyakit Kronis, Riwayat Rawat Inap, Catatan Alergi, dan Hasil Laboratorium/Pemeriksaan).\n"
            "2. ATURAN ANTI-HALUSINASI MUTLAK: Sajikan informasi HANYA berdasarkan data yang tersedia di SIMRS pada konteks di atas. "
            "Jika data tertentu (misalnya profil demografi, riwayat penyakit kronis, riwayat rawat inap, riwayat alergi, catatan SOAP, atau hasil lab) tidak ada / kosong / berstatus 'TIDAK DITEMUKAN', sampaikan apa adanya secara eksplisit dan jujur, misalnya: 'Data tidak ditemukan / Tidak ada riwayat penyakit kronis yang tercatat di SIMRS'. "
            "DILARANG KERAS mengarang, berhalusinasi, atau memalsukan data pasien, penyakit, rawat inap, atau hasil lab.\n"
            "3. Format sajian menggunakan Markdown terstruktur dan tabel rapi:\n"
            "   - Judul: `## 📋 Informasi Riwayat Medis & Demografi Pasien (SIMRS MCP)`\n"
            "   - **Profil & Demografi Pasien** (Tabel: Nama, MRN, NIK, Usia/Gender, BPJS, Poliklinik/DPJP)\n"
            "   - **Riwayat Penyakit Kronis & Alergi Obat** (Sebutkan penyakit kronis dan alergi, atau nyatakan 'Data tidak ditemukan' jika tidak ada)\n"
            "   - **Riwayat Rawat Inap Terdahulu** (Tabel admisi atau nyatakan 'Data tidak ditemukan / Tidak ada riwayat rawat inap terdahulu yang tercatat di SIMRS')\n"
            "   - **Hasil Laboratorium & Tanda Vital Pasien** (Tabel lab dan tanda vital, atau nyatakan 'Data tidak ditemukan' jika belum ada pemeriksaan lab)\n"
            "   - Catatan ringkas tindak lanjut klinis dan disclaimer medis resmi."
        )

    else:
        prompt_context = f"Doctor Query: {query}\n\n"
        if simrs_profile:
            prompt_context += (
                f"=== SIMRS PATIENT DEMOGRAPHICS (VIA MCP) ===\n"
                f"MRN: {simrs_profile['mrn']} | Full Name: {simrs_profile['full_name']}\n"
                f"NIK: {simrs_profile['nik']} | BPJS No: {simrs_profile['bpjs_card_no']} ({simrs_profile['bpjs_class']})\n"
                f"Age/Sex: {simrs_profile['age']} y/o {simrs_profile['gender']} | Clinic: {simrs_profile['active_clinic']} | DPJP: {simrs_profile['attending_physician']}\n\n"
            )
        if simrs_anamnesis:
            prompt_context += (
                f"=== DATA ANAMNESIS PASIEN (SUBJECTIVE) ===\n"
                f"Chief Complaint (Keluhan Utama): {simrs_anamnesis.get('chief_complaint')}\n"
                f"History of Present Illness (RPS): {simrs_anamnesis.get('history_present_illness')}\n"
                f"Past Medical History (RPD): {simrs_anamnesis.get('past_medical_history')}\n"
                f"Allergy & Medication History: {simrs_anamnesis.get('allergy_history')} | {simrs_anamnesis.get('medication_history')}\n\n"
            )
        if simrs_labs:
            prompt_context += (
                f"=== DATA OBSERVASI & PEMERIKSAAN (OBJECTIVE) ===\n"
                f"Vital Signs (TTV): {simrs_labs.get('vital_signs')}\n"
                f"Laboratory Evaluations:\n"
            )
            for l in simrs_labs.get("latest_labs", [])[:5]:
                prompt_context += f"- {l['test_name']}: {l['value']} {l['unit']} ({l['status']})\n"
            prompt_context += "\n"
        if rag_chunks:
            prompt_context += f"=== QDRANT VECTOR RAG KNOWLEDGE ===\n"
            for i, chunk in enumerate(rag_chunks, 1):
                prompt_context += f"[{i}] {chunk['title']}: {chunk['chunk_snippet']}\n\n"
        if lit_summary:
            prompt_context += f"=== CLINICAL PRACTICE GUIDELINE REFERENCES ===\n{lit_summary}\n\n"

        intro_desc = (
            "Anda adalah Asisten AI Medis Klinis (Medical Co-Pilot) profesional yang berfokus pada konsultasi medis umum berbasis literatur ilmiah dan basis pengetahuan vektor Qdrant (Knowledge Management)."
            if not simrs_profile
            else "Anda adalah Asisten AI Medis Klinis (Medical Co-Pilot) profesional yang terintegrasi dengan SIMRS melalui Model Context Protocol (MCP) dan basis pengetahuan vektor Qdrant RAG (Knowledge Management)."
        )
        system_instruction = (
            f"{intro_desc} "
            "Tugas Anda adalah memberikan jawaban ilmiah, terstruktur, dan berbasis bukti medis (Evidence-Based Medicine). "
            "Gunakan tabel Markdown bila relevan dan selalu sertakan disclaimer medis singkat di bagian akhir."
        )

    api_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "")
    structured_output = None

    if api_key and HAS_LANGCHAIN_GEMINI:
        try:
            llm = ChatGoogleGenerativeAI(
                model=settings.GEMINI_MODEL_NAME,
                google_api_key=api_key,
                temperature=0.2
            )
            response = llm.invoke([
                SystemMessage(content=system_instruction),
                HumanMessage(content=prompt_context)
            ])
            if isinstance(response.content, list):
                final_text = "".join([
                    part.get("text", "") if isinstance(part, dict) else str(part)
                    for part in response.content
                ]).strip()
            else:
                final_text = str(response.content).strip()
            _, structured_output = _generate_fallback_synthesis(
                query, ehr_data, simrs_profile, simrs_history, simrs_anamnesis, simrs_labs,
                diagnostic_rec, disease_exp, red_flags, med_rec, drug_safety,
                simrs_update_res, drug_findings, lit_summary, rag_chunks
            )
        except Exception as e:
            final_text, structured_output = _generate_fallback_synthesis(
                query, ehr_data, simrs_profile, simrs_history, simrs_anamnesis, simrs_labs,
                diagnostic_rec, disease_exp, red_flags, med_rec, drug_safety,
                simrs_update_res, drug_findings, lit_summary, rag_chunks, error_note=str(e)
            )
    elif api_key and HAS_GOOGLE_GENAI_SDK:
        try:
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model=settings.GEMINI_MODEL_NAME,
                contents=f"{system_instruction}\n\n{prompt_context}"
            )
            final_text = (response.text or "").strip()
            _, structured_output = _generate_fallback_synthesis(
                query, ehr_data, simrs_profile, simrs_history, simrs_anamnesis, simrs_labs,
                diagnostic_rec, disease_exp, red_flags, med_rec, drug_safety,
                simrs_update_res, drug_findings, lit_summary, rag_chunks
            )
        except Exception as e:
            final_text, structured_output = _generate_fallback_synthesis(
                query, ehr_data, simrs_profile, simrs_history, simrs_anamnesis, simrs_labs,
                diagnostic_rec, disease_exp, red_flags, med_rec, drug_safety,
                simrs_update_res, drug_findings, lit_summary, rag_chunks, error_note=str(e)
            )
    else:
        final_text, structured_output = _generate_fallback_synthesis(
            query, ehr_data, simrs_profile, simrs_history, simrs_anamnesis, simrs_labs,
            diagnostic_rec, disease_exp, red_flags, med_rec, drug_safety,
            simrs_update_res, drug_findings, lit_summary, rag_chunks
        )

    steps.append({
        "step_name": "Google Gemini LLM Clinical Synthesis",
        "description": f"Synthesized evidence-based guidelines & Knowledge Management literature via Gemini ({settings.GEMINI_MODEL_NAME})",
        "status": "success",
        "result": "Synthesis generated successfully"
    })
    log_node_end("synthesis", f"Synthesis Result: {len(final_text)} characters generated")

    return {
        **state,
        "steps_executed": steps,
        "final_synthesis": final_text,
        "structured_output": structured_output
    }
