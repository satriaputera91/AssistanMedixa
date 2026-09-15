"""
Clinical Planner Prompts and Function Calling Declarations for GenAI Intent Detection.
"""

from typing import Dict, Any, List

PLANNER_SYSTEM_INSTRUCTION = (
    "Anda adalah Clinical Intent Classifier & Orchestrator untuk Asisten Klinis AI (AssistantMedixa). "
    "Tugas utama Anda adalah menganalisis pertanyaan klinis dari dokter atau tenaga medis, "
    "lalu menentukan INTENT KLINIS yang paling tepat dengan memanggil fungsi `classify_clinical_intent`.\n\n"
    "Pedoman Penentuan Intent:\n"
    "1. Jika kueri dokter meminta informasi pasien, data demografi, nomor rekam medis (MRN), NIK, BPJS, atau profil pasien, "
    "pilihlah intent: '1. Ambil Informasi Demografi Pasien (SIMRS / Satu Sehat)'.\n"
    "2. Jika kueri meminta anamnesis, keluhan utama, atau riwayat penyakit: '2. Ambil Anamnesis Sebelumnya'.\n"
    "3. Jika kueri meminta hasil laboratorium, tanda vital, eGFR: '3. Evaluasi Hasil Lab & Pemeriksaan SIMRS (MCP)'.\n"
    "4. Jika kueri meminta diagnosis atau kode ICD-10: '4. Rekomendasi Diagnosis & ICD-10'.\n"
    "5. Jika kueri meminta rekomendasi obat, terapi farmakologi, dosis: '5. Rekomendasi Terapi Obat Berbasis Bukti (Knowledge Management)'.\n"
    "6. Jika kueri meminta tindakan medis/prosedur klinis: '6. Rekomendasi Tindakan & Prosedur Medis (Clinical Procedures & Interventions)'.\n"
    "7. Jika kueri meminta penjelasan patofisiologi/penyakit: '7. Penjelasan Penyakit & Patofisiologi (Knowledge Management)'.\n"
    "8. Jika kueri meminta deteksi tanda bahaya/kegawatdaruratan: '8. Deteksi Tanda Bahaya & Red Flags (Knowledge Management)'.\n"
    "9. Jika kueri meminta skrining interaksi obat atau kontraindikasi: '9. Skrining Interaksi & Keamanan Obat Pasien'.\n"
    "10. Jika kueri meminta pembuatan atau pengiriman catatan CPPT / SOAP ke SIMRS: '10. Buat Draft CPPT S/O/A/P'.\n"
    "11. Jika kueri meminta evaluasi menyeluruh: 'Evaluasi Klinis Terpadu SIMRS & Knowledge Management'.\n"
    "12. Jika tidak ada intent spesifik atau percakapan biasa: 'direct_conversation'."
)

PATIENT_INTENTS_LIST: List[str] = [
    "1. Ambil Informasi Demografi Pasien (SIMRS / Satu Sehat)",
    "2. Ambil Anamnesis Sebelumnya",
    "3. Evaluasi Hasil Lab & Pemeriksaan SIMRS (MCP)",
    "4. Rekomendasi Diagnosis & ICD-10",
    "5. Rekomendasi Terapi Obat Berbasis Bukti (Knowledge Management)",
    "6. Rekomendasi Tindakan & Prosedur Medis (Clinical Procedures & Interventions)",
    "7. Penjelasan Penyakit & Patofisiologi (Knowledge Management)",
    "8. Deteksi Tanda Bahaya & Red Flags (Knowledge Management)",
    "9. Skrining Interaksi & Keamanan Obat Pasien",
    "10. Buat Draft CPPT S/O/A/P",
    "Evaluasi Klinis Terpadu SIMRS & Knowledge Management",
    "direct_conversation"
]

GENERAL_INTENTS_LIST: List[str] = [
    "1. Pedoman Klinis & Kriteria Diagnosis (Knowledge Management)",
    "2. Panduan Terapi & Rejimen Lini Pertama (Knowledge Management)",
    "3. Panduan Tindakan & Prosedur Medis (Clinical Guidelines)",
    "4. Penyesuaian Dosis Ginjal & Hepar (Knowledge Management)",
    "5. Skrining Interaksi Obat & Kontraindikasi (Knowledge Management)",
    "6. Deteksi Tanda Bahaya & Kedaruratan (Knowledge Management)",
    "7. Interpretasi Biomarker & Hasil Lab (Knowledge Management)",
    "8. Penjelasan Patofisiologi & Mekanisme Penyakit (Knowledge Management)",
    "direct_conversation"
]

CLASSIFY_INTENT_FUNCTION_DECLARATION: Dict[str, Any] = {
    "name": "classify_clinical_intent",
    "description": (
        "Mengklasifikasikan kueri klinis dokter ke dalam intent alur kerja terstruktur "
        "untuk mengarahkan eksekusi simpul agen medis secara optimal."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "intent": {
                "type": "STRING",
                "description": "Nama intent klinis yang dipilih dari daftar intent yang tersedia.",
                "enum": list(set(PATIENT_INTENTS_LIST + GENERAL_INTENTS_LIST))
            },
            "reasoning": {
                "type": "STRING",
                "description": "Alasan penalaran klinis singkat atas penentuan intent tersebut."
            },
            "confidence": {
                "type": "NUMBER",
                "description": "Skor keyakinan klasifikasi antara 0.0 hingga 1.0."
            },
            "is_demographic_inquiry": {
                "type": "BOOLEAN",
                "description": "True bila pertanyaan dokter semata-mata meminta data identitas atau profil demografi pasien."
            }
        },
        "required": ["intent", "reasoning"]
    }
}


def build_planner_prompt(user_query: str, patient_id: str = None, patient_name: str = None) -> str:
    """Constructs prompt for Gemini GenAI intent classification."""
    context_lines = [
        f"Kueri Dokter: \"{user_query}\"",
    ]
    if patient_id and patient_id.strip():
        pat_str = f"{patient_id} ({patient_name})" if patient_name else patient_id
        context_lines.append(f"Konteks Pasien Aktif: {pat_str} (SIMRS Mode)")
        context_lines.append("Tersedia Daftar Intent Pasien (1-10, Evaluasi Terpadu, atau direct_conversation).")
    else:
        context_lines.append("Konteks: Konsultasi Medis Umum (Tanpa Pasien Aktif / Knowledge Management Mode)")
        context_lines.append("Tersedia Daftar Intent Umum (1-8 Pedoman/Literatur, atau direct_conversation).")

    context_lines.append(
        "\nKlasifikasikan kueri di atas sekarang dengan memanggil fungsi `classify_clinical_intent`."
    )
    return "\n".join(context_lines)
