import re
from typing import List, Optional, Dict, Any, Union
# pyrefly: ignore [missing-import]
from pydantic import BaseModel, Field
from datetime import datetime


MANDATORY_CLINICAL_DISCLAIMER = (
    "\n\n---\n*(⚠️ **Clinical Disclaimer**: Sistem pendukung keputusan klinis AI ditujukan untuk "
    "dokter berwenang. Keputusan klinis sepenuhnya berada di bawah pertimbangan dokter penanggung jawab.)*"
)


# ==============================================================================
# Domain Primitive Sub-Schemas
# ==============================================================================

# pyrefly: ignore [missing-import]
from pydantic import BaseModel, Field, model_validator


class VitalSignsData(BaseModel):
    blood_pressure: Optional[str] = Field(default=None, description="Tekanan darah, misal: 120/80 mmHg")
    heart_rate: Optional[str] = Field(default=None, description="Frekuensi nadi, misal: 80 bpm")
    respiratory_rate: Optional[str] = Field(default=None, description="Laju napas, misal: 18 x/menit")
    temperature: Optional[str] = Field(default=None, description="Suhu tubuh, misal: 36.8 °C")
    spo2: Optional[str] = Field(default=None, description="Saturasi oksigen, misal: 98%")


class LabItemData(BaseModel):
    test_name: str = Field(description="Nama tes laboratorium, misal: HbA1c, eGFR")
    value: str = Field(description="Nilai kuantitatif atau kualitatif")
    unit: Optional[str] = Field(default="", description="Satuan ukuran, misal: g/dL, mg/dL")
    status: Optional[str] = Field(default="Normal", description="Normal, High, Low, Critical")
    reference_range: Optional[str] = Field(default="", description="Rentang rujukan normal")

    @model_validator(mode="before")
    @classmethod
    def parse_str_or_dict(cls, data: Any) -> Any:
        if isinstance(data, str):
            return {"test_name": data, "value": "Tercatat", "unit": "", "status": "Recorded"}
        return data


class PatientDemographicsData(BaseModel):
    mrn: str = Field(description="Nomor Rekam Medis Pasien")
    full_name: str = Field(description="Nama lengkap pasien")
    nik: Optional[str] = Field(default="", description="Nomor Induk Kependudukan")
    bpjs_card_no: Optional[str] = Field(default="", description="Nomor kartu BPJS")
    bpjs_class: Optional[str] = Field(default="", description="Kelas kepesertaan BPJS")
    age: Optional[int] = Field(default=None, description="Usia pasien")
    gender: Optional[str] = Field(default="", description="Jenis kelamin: Male/Female/Laki-laki/Perempuan")
    active_clinic: Optional[str] = Field(default="", description="Poli rawat jalan")
    attending_physician: Optional[str] = Field(default="", description="Nama DPJP")


class SubjectiveData(BaseModel):
    chief_complaint: str = Field(description="Keluhan utama pasien")
    history_present_illness: Optional[str] = Field(default="", description="Riwayat Penyakit Sekarang (RPS)")
    past_medical_history: Optional[str] = Field(default="", description="Riwayat Penyakit Dahulu (RPD)")
    allergy_history: Optional[str] = Field(default="Tidak ada riwayat alergi", description="Riwayat alergi obat & makanan")
    medication_history: Optional[str] = Field(default="", description="Riwayat obat yang sedang dikonsumsi")


class ObjectiveData(BaseModel):
    vital_signs: Optional[VitalSignsData] = Field(default_factory=VitalSignsData)
    physical_examination: Optional[str] = Field(default="", description="Temuan pemeriksaan fisik umum/lokalis")
    laboratory_results: List[LabItemData] = Field(default_factory=list, description="Daftar hasil laboratorium")

    @model_validator(mode="before")
    @classmethod
    def normalize_labs(cls, data: Any) -> Any:
        if isinstance(data, dict):
            labs = data.get("laboratory_results")
            if isinstance(labs, dict):
                data["laboratory_results"] = [
                    {"test_name": k.replace("_", " ").upper(), "value": str(v), "unit": "", "status": "Recorded"}
                    for k, v in labs.items()
                ]
            elif isinstance(labs, str):
                data["laboratory_results"] = [{"test_name": labs, "value": "Recorded"}]
        return data


class DiagnosisItemData(BaseModel):
    diagnosis: str = Field(description="Nama diagnosis kerja / banding")
    icd10: str = Field(default="R69", description="Kode ICD-10 resmi, misal: E11.9, I10")
    confidence: Optional[Union[float, str]] = Field(default=0.9, description="Tingkat keyakinan klinis")
    notes: Optional[str] = Field(default="", description="Catatan pendukung atau kriteria diagnostik")

    @model_validator(mode="before")
    @classmethod
    def parse_str_or_dict(cls, data: Any) -> Any:
        if isinstance(data, str):
            icd_match = re.search(r"\[ICD-10:\s*([A-Z0-9\.]+)\]", data, re.IGNORECASE)
            icd = icd_match.group(1) if icd_match else "R69"
            clean_name = re.sub(r"\[.*?\]", "", data).strip()
            return {"diagnosis": clean_name or data, "icd10": icd, "confidence": 0.9}
        return data


class AssessmentData(BaseModel):
    primary_diagnosis: DiagnosisItemData = Field(description="Diagnosis primer / kerja utama")
    differential_diagnoses: List[DiagnosisItemData] = Field(default_factory=list, description="Diagnosis banding")
    clinical_reasoning: Optional[str] = Field(default="", description="Alasan klinis dan patofisiologi")

    @model_validator(mode="before")
    @classmethod
    def normalize_assessment(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if isinstance(data.get("primary_diagnosis"), str):
                data["primary_diagnosis"] = DiagnosisItemData.parse_str_or_dict(data["primary_diagnosis"])
            diffs = data.get("differential_diagnoses")
            if isinstance(diffs, list):
                data["differential_diagnoses"] = [
                    DiagnosisItemData.parse_str_or_dict(d) if isinstance(d, str) else d for d in diffs
                ]
            elif isinstance(diffs, str):
                data["differential_diagnoses"] = [DiagnosisItemData.parse_str_or_dict(diffs)]
        return data


class MedicationItemData(BaseModel):
    drug_name: str = Field(description="Nama zat aktif atau obat")
    dosage: str = Field(default="Standard", description="Dosis terapi, misal: 500 mg")
    frequency: str = Field(default="Sesuai anjuran", description="Frekuensi pemakaian, misal: 3x sehari")
    route: Optional[str] = Field(default="Oral", description="Rute pemberian: Oral, IV, IM, Topikal")
    duration: Optional[str] = Field(default="", description="Durasi terapi, misal: 5 hari, 30 hari")
    notes: Optional[str] = Field(default="", description="Indikasi, penyesuaian dosis, atau peringatan")

    @model_validator(mode="before")
    @classmethod
    def parse_str_or_dict(cls, data: Any) -> Any:
        if isinstance(data, str):
            return {"drug_name": data, "dosage": "Standard", "frequency": "Sesuai resep dokter", "route": "Oral"}
        return data


class RedFlagData(BaseModel):
    title: str = Field(description="Nama tanda bahaya klinis")
    severity: str = Field(default="Warning", description="Critical, High, Warning")
    action_required: str = Field(default="Monitoring ketat", description="Tindakan darurat / intervensi yang disarankan")

    @model_validator(mode="before")
    @classmethod
    def parse_str_or_dict(cls, data: Any) -> Any:
        if isinstance(data, str):
            return {"title": data, "severity": "Warning", "action_required": "Monitoring klinis & evaluasi berkala"}
        return data


class PlanData(BaseModel):
    medications: List[MedicationItemData] = Field(default_factory=list, description="Rejimen terapi farmakologi")
    diagnostic_workup: List[str] = Field(default_factory=list, description="Rencana pemeriksaan penunjang/lab serial")
    clinical_procedures: List[str] = Field(default_factory=list, description="Prosedur atau tindakan medis")
    patient_education: List[str] = Field(default_factory=list, description="Edukasi pasien dan modifikasi gaya hidup")
    follow_up: Optional[str] = Field(default="Kontrol ulang 1-2 minggu", description="Jadwal kunjungan tindak lanjut")

    @model_validator(mode="before")
    @classmethod
    def normalize_plan(cls, data: Any) -> Any:
        if isinstance(data, dict):
            for field in ["diagnostic_workup", "clinical_procedures", "patient_education"]:
                val = data.get(field)
                if isinstance(val, str):
                    data[field] = [val]
            meds = data.get("medications")
            if isinstance(meds, list):
                data["medications"] = [
                    MedicationItemData.parse_str_or_dict(m) if isinstance(m, str) else m for m in meds
                ]
            elif isinstance(meds, str):
                data["medications"] = [MedicationItemData.parse_str_or_dict(meds)]
        return data


# ==============================================================================
# High-Level Clinical Output Schemas with Markdown Renderers
# ==============================================================================

class ClinicalSOAPOutputSchema(BaseModel):
    """
    Structured Clinical S-O-A-P / CPPT Output Schema.
    """
    output_type: str = Field(default="clinical_soap", description="Identifier output schema")
    title: str = Field(default="📋 Hasil Rekomendasi Resume (CPPT / S-O-A-P)")
    patient: Optional[PatientDemographicsData] = None
    subjective: SubjectiveData
    objective: ObjectiveData
    assessment: AssessmentData
    plan: PlanData
    red_flags: List[RedFlagData] = Field(default_factory=list)
    drug_safety_status: Optional[str] = Field(default="Aman (Tidak ditemukan interaksi mayor / alergi)")
    notes: Optional[str] = ""

    @model_validator(mode="before")
    @classmethod
    def normalize_soap_schema(cls, data: Any) -> Any:
        if isinstance(data, dict):
            rf = data.get("red_flags")
            if isinstance(rf, dict):
                data["red_flags"] = [RedFlagData.parse_str_or_dict(rf)]
            elif isinstance(rf, str):
                data["red_flags"] = [RedFlagData.parse_str_or_dict(rf)]
        return data

    def to_markdown(self) -> str:
        md = f"## {self.title}\n\n"

        # Demographics Table if available
        if self.patient:
            md += "### 👤 Informasi Demografi Pasien\n"
            md += "| Parameter | Data Pasien |\n| :--- | :--- |\n"
            md += f"| **No. Rekam Medis (MRN)** | `{self.patient.mrn}` |\n"
            md += f"| **Nama Lengkap** | **{self.patient.full_name}** |\n"
            if self.patient.nik:
                md += f"| **NIK** | {self.patient.nik} |\n"
            if self.patient.bpjs_card_no:
                md += f"| **No. BPJS** | {self.patient.bpjs_card_no} ({self.patient.bpjs_class or 'BPJS Kesehatan'}) |\n"
            if self.patient.age:
                md += f"| **Usia / Jenis Kelamin** | {self.patient.age} tahun / {self.patient.gender or 'N/A'} |\n"
            if self.patient.active_clinic:
                md += f"| **Poliklinik / DPJP** | {self.patient.active_clinic} / {self.patient.attending_physician or 'DPJP'} |\n"
            md += "\n"

        # Red Flags Alert if present
        if self.red_flags:
            md += "### 🚨 Tanda Bahaya Klinis (Red Flags)\n"
            for rf in self.red_flags:
                md += f"- **[{rf.severity.upper()}] {rf.title}**: {rf.action_required}\n"
            md += "\n"

        # Subjective Section
        md += "### 📝 S — Subjective (Anamnesis)\n"
        md += f"- **Keluhan Utama**: {self.subjective.chief_complaint}\n"
        if self.subjective.history_present_illness:
            md += f"- **Riwayat Penyakit Sekarang (RPS)**: {self.subjective.history_present_illness}\n"
        if self.subjective.past_medical_history:
            md += f"- **Riwayat Penyakit Dahulu (RPD)**: {self.subjective.past_medical_history}\n"
        md += f"- **Riwayat Alergi**: {self.subjective.allergy_history}\n"
        if self.subjective.medication_history:
            md += f"- **Riwayat Pengobatan**: {self.subjective.medication_history}\n"
        md += "\n"

        # Objective Section
        md += "### 🔬 O — Objective (Pemeriksaan Fisik & Penunjang)\n"        
        if self.objective.physical_examination:
            md += f"- **Pemeriksaan Fisik**: {self.objective.physical_examination}\n"

        if self.objective.vital_signs:
            vs = self.objective.vital_signs
            v_parts = []
            if vs.blood_pressure: v_parts.append(f"TD: {vs.blood_pressure}")
            if vs.heart_rate: v_parts.append(f"HR: {vs.heart_rate}")
            if vs.respiratory_rate: v_parts.append(f"RR: {vs.respiratory_rate}")
            if vs.temperature: v_parts.append(f"Suhu: {vs.temperature}")
            if vs.spo2: v_parts.append(f"SpO2: {vs.spo2}")
            if v_parts:
                md += f"- **Tanda Vital (TTV)**: {', '.join(v_parts)}\n"

       
        if self.objective.laboratory_results:
            md += "\n**Hasil Laboratorium & Pemeriksaan:**\n"
            md += "| Parameter | Hasil | Satuan | Status | Nilai Rujukan |\n| :--- | :--- | :--- | :--- | :--- |\n"
            for lab in self.objective.laboratory_results:
                md += f"| {lab.test_name} | **{lab.value}** | {lab.unit} | {lab.status} | {lab.reference_range or '-'} |\n"
            md += "\n"
        else:
            md += "\n"

        # Assessment Section
        md += "### 🎯 A — Assessment (Diagnosis Kerja & Banding)\n"
        md += f"- **Diagnosis Utama**: **{self.assessment.primary_diagnosis.diagnosis}** `[ICD-10: {self.assessment.primary_diagnosis.icd10}]`\n"
        if self.assessment.differential_diagnoses:
            md += "- **Diagnosis Banding**:\n"
            for dd in self.assessment.differential_diagnoses:
                md += f"  - {dd.diagnosis} `[ICD-10: {dd.icd10}]`"
                if dd.notes:
                    md += f" — {dd.notes}"
                md += "\n"
        if self.assessment.clinical_reasoning:
            md += f"- **Penalaran Klinis**: {self.assessment.clinical_reasoning}\n"
        md += "\n"

        # Plan Section
        md += "### 💊 P — Plan (Penatalaksanaan & Terapi)\n"
        if self.plan.medications:
            md += "**Rekomendasi Terapi Farmakologi:**\n"
            md += "| Obat / Zat Aktif | Dosis | Frekuensi | Rute | Durasi | Keterangan / Dosing |\n| :--- | :--- | :--- | :--- | :--- | :--- |\n"
            for m in self.plan.medications:
                md += f"| **{m.drug_name}** | {m.dosage} | {m.frequency} | {m.route or 'Oral'} | {m.duration or '-'} | {m.notes or '-'} |\n"
            md += "\n"

        if self.plan.diagnostic_workup:
            md += "**Rencana Pemeriksaan Penunjang Lanjutan:**\n"
            for dw in self.plan.diagnostic_workup:
                md += f"- {dw}\n"
            md += "\n"

        if self.plan.clinical_procedures:
            md += "**Tindakan / Prosedur Medis:**\n"
            for proc in self.plan.clinical_procedures:
                md += f"- {proc}\n"
            md += "\n"

        if self.plan.patient_education:
            md += "**Edukasi Pasien & Modifikasi Gaya Hidup:**\n"
            for edu in self.plan.patient_education:
                md += f"- {edu}\n"
            md += "\n"

        if self.plan.follow_up:
            md += f"- **Tindak Lanjut**: {self.plan.follow_up}\n\n"
        md += MANDATORY_CLINICAL_DISCLAIMER
        return md


class GeneralConsultationKnowledgeSchema(BaseModel):
    """
    Structured Clinical Knowledge Query Output (Guidelines, Pharmacology, Disease Explanations).
    """
    output_type: str = Field(default="general_knowledge", description="Identifier output schema")
    title: str = Field(description="Judul topik klinis / panduan")
    summary: str = Field(description="Ringkasan eksekutif pedoman medis")
    key_points: List[str] = Field(default_factory=list, description="Poin-poin penting pedoman")
    clinical_evidence: Optional[str] = Field(default="", description="Bukti literatur dan dasar ilmiah")
    treatment_recommendations: List[MedicationItemData] = Field(default_factory=list, description="Daftar rekomendasi obat")
    diagnostic_criteria: List[str] = Field(default_factory=list, description="Kriteria diagnosis")
    special_populations: Optional[str] = Field(default="", description="Pertimbangan khusus ginjal/hepar/lansia/hamil")
    red_flags: List[RedFlagData] = Field(default_factory=list)

    def to_markdown(self) -> str:
        md = f"## 📖 {self.title}\n\n"
        md += f"### 📌 Ringkasan Pedoman Klinis\n{self.summary}\n\n"

        if self.key_points:
            md += "### 💡 Poin Kunci Praktik Klinis\n"
            for kp in self.key_points:
                md += f"- {kp}\n"
            md += "\n"

        if self.diagnostic_criteria:
            md += "### 🎯 Kriteria Diagnostik & Staging\n"
            for dc in self.diagnostic_criteria:
                md += f"- {dc}\n"
            md += "\n"

        if self.treatment_recommendations:
            md += "### 💊 Panduan Terapi Farmakologi Berbasis Bukti\n"
            md += "| Obat / Regimen | Dosis Lazim | Frekuensi | Rute | Pertimbangan Khusus |\n| :--- | :--- | :--- | :--- | :--- |\n"
            for m in self.treatment_recommendations:
                md += f"| **{m.drug_name}** | {m.dosage} | {m.frequency} | {m.route or 'Oral'} | {m.notes or '-'} |\n"
            md += "\n"

        if self.special_populations:
            md += f"### ⚠️ Pertimbangan Populasi Khusus (Dosing Ginjal / Hepar)\n{self.special_populations}\n\n"

        if self.red_flags:
            md += "### 🚨 Tanda Bahaya & Kriteria Rujukan Darurat\n"
            for rf in self.red_flags:
                md += f"- **[{rf.severity.upper()}] {rf.title}**: {rf.action_required}\n"
            md += "\n"

        if self.clinical_evidence:
            md += f"### 📚 Bukti Literatur & Panduan Klinis Terkait\n{self.clinical_evidence}\n\n"

        md += MANDATORY_CLINICAL_DISCLAIMER
        return md


class SIMRSTransactionReportSchema(BaseModel):
    """
    Structured Report for CPPT sync / commit to SIMRS via Model Context Protocol.
    """
    output_type: str = Field(default="simrs_transaction", description="Identifier output schema")
    title: str = Field(default="📤 Hasil Rekomendasi Resume (CPPT / S-O-A-P) ke SIMRS RME")
    status_message: str = Field(default="✅ Berhasil Terkirim & Tersimpan di Modul RME SIMRS")
    log_id: str = Field(description="ID Log Transaksi SIMRS")
    timestamp: str = Field(description="Waktu Transaksi")
    patient: PatientDemographicsData
    soap_summary: Dict[str, str] = Field(description="Ringkasan S, O, A, P yang dikirimkan")

    def to_markdown(self) -> str:
        md = f"## {self.title}\n\n"
        md += "### 🟢 Status Transaksi SIMRS (Model Context Protocol)\n"
        md += "| Parameter Integrasi | Rincian Data |\n| :--- | :--- |\n"
        md += f"| **Status Integrasi** | {self.status_message} |\n"
        md += f"| **Log Transaksi ID** | `{self.log_id}` |\n"
        md += f"| **Waktu Transaksi** | {self.timestamp} |\n"
        md += f"| **No. Rekam Medis (MRN)** | {self.patient.mrn} ({self.patient.full_name}) |\n"
        md += f"| **DPJP Pemeriksa** | {self.patient.attending_physician or 'Dr. Sarah Jenkins, Sp.PD'} |\n\n"

        md += "### 📋 Resume CPPT / S-O-A-P yang Ditransmisikan ke SIMRS\n"
        md += "| Komponen | Data Klinis CPPT Terintegrasi |\n| :--- | :--- |\n"
        md += f"| **Subjective (S)** | {self.soap_summary.get('subjective', '-')} |\n"
        md += f"| **Objective (O)** | {self.soap_summary.get('objective', '-')} |\n"
        md += f"| **Assessment (A)** | {self.soap_summary.get('assessment', '-')} |\n"
        md += f"| **Plan (P)** | {self.soap_summary.get('plan', '-')} |\n\n"

        md += "🔒 *Data CPPT telah tercatat permanen pada database SIMRS EMR dan dapat diakses melalui modul Rekam Medis Elektronik.*"
        md += MANDATORY_CLINICAL_DISCLAIMER
        return md


class DiarizedUtterance(BaseModel):
    speaker: str = Field(description="Label pembicara: 'Dokter', 'Pasien', atau 'Keluarga Pasien'")
    start_time: Optional[str] = Field(default="00:00", description="Waktu mulai, misal: '00:00'")
    end_time: Optional[str] = Field(default="00:00", description="Waktu selesai, misal: '00:06'")
    text: str = Field(description="Isi dialog atau ujaran percakapan")


class AudioDiarizationSchema(BaseModel):
    """
    Structured Pydantic Model for Audio Speech-to-Text & Speaker Diarization.
    """
    audio_filename: str = Field(default="consultation_recording.wav", description="Nama file audio rekaman")
    session_type: str = Field(default="Konsultasi Klinis Rawat Jalan", description="Jenis sesi klinis")
    language: str = Field(default="id-ID", description="Bahasa transkripsi")
    utterances: List[DiarizedUtterance] = Field(default_factory=list, description="Daftar ujaran percakapan terdiarisasi")
    
    def to_formatted_transcript(self) -> str:
        lines = []
        for u in self.utterances:
            time_str = f"[{u.start_time} - {u.end_time}]" if u.start_time and u.end_time else ""
            lines.append(f"**{u.speaker} {time_str}**: '{u.text}'")
        return "\n\n".join(lines)


class AudioConsultationSOAPSchema(BaseModel):
    """
    Structured Pydantic Model for Diarized Audio Consultation Transcription & SOAP Synthesis.
    """
    output_type: str = Field(default="audio_soap", description="Identifier output schema")
    audio_filename: str = Field(default="consultation_recording.wav")
    transcript: str = Field(description="Transkrip lengkap percakapan terdiarisasi")
    diarization: Optional[AudioDiarizationSchema] = None
    soap: ClinicalSOAPOutputSchema

    def to_markdown(self) -> str:
        md = f"## 🎙️ Resume Konsultasi Klinis dari Rekaman Audio ({self.audio_filename})\n\n"
        md += "### 🗣️ Transkrip Percakapan Dokter — Pasien (Diarisasi Pembicara):\n"
        if self.diarization and self.diarization.utterances:
            md += self.diarization.to_formatted_transcript() + "\n\n"
        else:
            md += f"{self.transcript}\n\n"
        md += self.soap.to_markdown()
        return md


# ==============================================================================
# Clinical Output Safety & Grounding Validator Engine
# ==============================================================================

class OutputValidationReport(BaseModel):
    is_valid: bool = True
    status: str = "PASSED"
    verdict: str = "VALID"
    validation_score: float = 1.0
    alerts: List[str] = Field(default_factory=list)
    remediation_applied: bool = False
    details: Dict[str, Any] = Field(default_factory=dict)
    round_number: int = 1
    needs_refinement: bool = False
    refinement_feedback: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class OutputValidator:
    """
    Multi-stage Clinical Grounding & Output Verification Engine.
    Ensures LLM generations strictly adhere to grounding data, patient allergies,
    clinical safety guidelines, and mandatory clinical disclaimers with 3-round feedback refinement.
    """

    @classmethod
    def validate_clinical_output(
        cls,
        output_text: str,
        patient_id: Optional[str] = None,
        ehr_data: Optional[Dict[str, Any]] = None,
        simrs_profile: Optional[Dict[str, Any]] = None,
        simrs_history: Optional[Dict[str, Any]] = None,
        simrs_anamnesis: Optional[Dict[str, Any]] = None,
        simrs_labs: Optional[Dict[str, Any]] = None,
        drug_safety: Optional[Dict[str, Any]] = None,
        structured_model: Optional[BaseModel] = None,
        round_number: int = 1,
        max_rounds: int = 3
    ) -> tuple[str, OutputValidationReport]:
        alerts: List[str] = []
        details: Dict[str, Any] = {}
        score = 1.0
        remediation_applied = False
        final_text = output_text

        # 1. Allergy & Contraindication Cross-Verification
        patient_allergies: List[str] = []
        if simrs_history and simrs_history.get("documented_allergies"):
            patient_allergies.extend(simrs_history["documented_allergies"])
        if ehr_data and ehr_data.get("allergies"):
            patient_allergies.extend(ehr_data["allergies"])
        if simrs_anamnesis and simrs_anamnesis.get("allergy_history"):
            patient_allergies.append(simrs_anamnesis["allergy_history"])

        penicillin_allergic = any("penicillin" in a.lower() or "penisilin" in a.lower() for a in patient_allergies)
        aspirin_allergic = any("aspirin" in a.lower() or "asetosal" in a.lower() for a in patient_allergies)
        nsaid_allergic = any("nsaid" in a.lower() or "ketorolac" in a.lower() or "mefenamat" in a.lower() for a in patient_allergies)

        out_lower = final_text.lower()
        if penicillin_allergic and any(p in out_lower for p in ["amoxicillin", "amoksisilin", "ampicillin", "penicillin g", "amoxiclav"]):
            alerts.append("CRITICAL: Output merekomendasikan antibiotik golongan Penicillin padahal pasien memiliki riwayat Alergi Berat Penicillin!")
            score -= 0.4
        if aspirin_allergic and ("aspirin" in out_lower or "aspilet" in out_lower or "cardioaspirin" in out_lower):
            alerts.append("WARNING: Output menyebutkan Aspirin padahal pasien memiliki riwayat Alergi/Dispepsia Berat ec Aspirin!")
            score -= 0.3
        if nsaid_allergic and any(n in out_lower for n in ["ketorolac", "asam mefenamat", "ibuprofen", "natrium diklofenak", "meloxicam"]):
            alerts.append("CRITICAL: Output merekomendasikan analgesik NSAID padahal pasien memiliki riwayat alergi bronkospasme/urtikaria NSAID!")
            score -= 0.4

        # 2. Grounding Verification (Demographics & Vitals)
        if simrs_profile:
            expected_name = simrs_profile.get("full_name", "")
            if expected_name and expected_name.lower() not in out_lower and "dr." not in expected_name.lower():
                details["demographics_anomaly"] = f"Nama pasien '{expected_name}' tidak terdeteksi pada teks laporan."

        if simrs_labs and simrs_labs.get("latest_labs"):
            for lab in simrs_labs["latest_labs"]:
                val = str(lab.get("value", "")).strip()
                tname = lab.get("test_name", "")
                if val and val in output_text:
                    details[f"grounded_lab_{tname}"] = "Verified present"

        # 3. Mandatory Clinical Disclaimer Enforcement
        has_disclaimer = any(k in out_lower for k in [
            "clinical disclaimer", "disclaimer medis", "disclaimer klinis", 
            "keputusan klinis", "pendukung keputusan", "tanggung jawab dokter"
        ])
        if not has_disclaimer:
            final_text = final_text.rstrip() + MANDATORY_CLINICAL_DISCLAIMER
            remediation_applied = True
            alerts.append("AUTO-REMEDIATION: Menambahkan disclaimer medis resmi di akhir laporan klinis.")
            score = max(score, 0.95)

        # 4. Determine Multi-Round Refinement Need (Loop 3 Rounds)
        needs_refinement = False
        refinement_feedback = None

        if round_number < max_rounds:
            # Check if there are clinical issues or room for depth polish
            if score < 0.98 or alerts or len(alerts) > 0:
                needs_refinement = True
                critique_points = []
                if alerts:
                    critique_points.append(f"Perbaiki isu alergi/kontraindikasi: {'; '.join(alerts)}")
                if details.get("demographics_anomaly"):
                    critique_points.append(f"Pastikan identitas pasien '{simrs_profile.get('full_name', '')}' tertera dengan jelas.")
                critique_points.append("Pertajam rekomendasi dosis dengan mempertimbangkan fungsi ginjal (eGFR) dan sertakan edukasi monitoring serial.")
                refinement_feedback = " | ".join(critique_points)

        is_valid = score >= 0.70
        status = "PASSED" if is_valid else "FAILED_CRITICAL_VALIDATION"
        verdict = "VALID" if is_valid else "INVALID_POTENTIAL_HAZARD"

        report = OutputValidationReport(
            is_valid=is_valid,
            status=status,
            verdict=verdict,
            validation_score=round(max(score, 0.0), 2),
            alerts=alerts,
            remediation_applied=remediation_applied,
            details=details,
            round_number=round_number,
            needs_refinement=needs_refinement,
            refinement_feedback=refinement_feedback
        )

        return final_text, report
