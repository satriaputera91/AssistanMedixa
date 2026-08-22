import re
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

MANDATORY_CLINICAL_DISCLAIMER = (
    "\n\n---\n*(⚠️ **Clinical Disclaimer**: Sistem pendukung keputusan klinis AI ditujukan untuk "
    "dokter berwenang. Keputusan klinis sepenuhnya berada di bawah pertimbangan dokter penanggung jawab.)*"
)


# ==============================================================================
# Domain Primitive Sub-Schemas
# ==============================================================================

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


class DiagnosisItemData(BaseModel):
    diagnosis: str = Field(description="Nama diagnosis kerja / banding")
    icd10: str = Field(description="Kode ICD-10 resmi, misal: E11.9, I10")
    confidence: Optional[float] = Field(default=0.9, ge=0.0, le=1.0, description="Tingkat keyakinan klinis")
    notes: Optional[str] = Field(default="", description="Catatan pendukung atau kriteria diagnostik")


class AssessmentData(BaseModel):
    primary_diagnosis: DiagnosisItemData = Field(description="Diagnosis primer / kerja utama")
    differential_diagnoses: List[DiagnosisItemData] = Field(default_factory=list, description="Diagnosis banding")
    clinical_reasoning: Optional[str] = Field(default="", description="Alasan klinis dan patofisiologi")


class MedicationItemData(BaseModel):
    drug_name: str = Field(description="Nama zat aktif atau obat")
    dosage: str = Field(description="Dosis terapi, misal: 500 mg")
    frequency: str = Field(description="Frekuensi pemakaian, misal: 3x sehari")
    route: Optional[str] = Field(default="Oral", description="Rute pemberian: Oral, IV, IM, Topikal")
    duration: Optional[str] = Field(default="", description="Durasi terapi, misal: 5 hari, 30 hari")
    notes: Optional[str] = Field(default="", description="Indikasi, penyesuaian dosis, atau peringatan")


class RedFlagData(BaseModel):
    title: str = Field(description="Nama tanda bahaya klinis")
    severity: str = Field(default="Warning", description="Critical, High, Warning")
    action_required: str = Field(description="Tindakan darurat / intervensi yang disarankan")


class PlanData(BaseModel):
    medications: List[MedicationItemData] = Field(default_factory=list, description="Rejimen terapi farmakologi")
    diagnostic_workup: List[str] = Field(default_factory=list, description="Rencana pemeriksaan penunjang/lab serial")
    clinical_procedures: List[str] = Field(default_factory=list, description="Prosedur atau tindakan medis")
    patient_education: List[str] = Field(default_factory=list, description="Edukasi pasien dan modifikasi gaya hidup")
    follow_up: Optional[str] = Field(default="Kontrol ulang 1-2 minggu", description="Jadwal kunjungan tindak lanjut")


# ==============================================================================
# High-Level Clinical Output Schemas with Markdown Renderers
# ==============================================================================

class ClinicalSOAPOutputSchema(BaseModel):
    """
    Structured Clinical S-O-A-P / CPPT Output Schema.
    """
    output_type: str = Field(default="clinical_soap", description="Identifier output schema")
    title: str = Field(default="📋 Catatan Perkembangan Pasien Terintegrasi (CPPT / S-O-A-P)")
    patient: Optional[PatientDemographicsData] = None
    subjective: SubjectiveData
    objective: ObjectiveData
    assessment: AssessmentData
    plan: PlanData
    red_flags: List[RedFlagData] = Field(default_factory=list)
    drug_safety_status: Optional[str] = Field(default="Aman (Tidak ditemukan interaksi mayor / alergi)")
    notes: Optional[str] = ""

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

        if self.objective.physical_examination:
            md += f"- **Pemeriksaan Fisik**: {self.objective.physical_examination}\n"

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

        if self.drug_safety_status:
            md += f"🛡️ **Status Skrining Keamanan Obat**: {self.drug_safety_status}\n"

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
    title: str = Field(default="📤 Pengiriman Catatan Perkembangan Pasien Terintegrasi (CPPT / S-O-A-P) ke SIMRS RME")
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


class AudioConsultationSOAPSchema(BaseModel):
    """
    Structured Schema for Audio Consultation Transcription & SOAP Synthesis.
    """
    output_type: str = Field(default="audio_soap", description="Identifier output schema")
    audio_filename: str
    transcript: str
    soap: ClinicalSOAPOutputSchema

    def to_markdown(self) -> str:
        md = f"## 🎙️ Rekaman Konsultasi Klinis ({self.audio_filename})\n\n"
        md += "### 🗣️ Transkrip Percakapan Dokter — Pasien\n"
        md += f"{self.transcript}\n\n"
        md += self.soap.to_markdown()
        return md
