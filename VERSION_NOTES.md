# 📋 Version Notes - AssistanMedixa (AIMedical)

---

## 🚀 Versi 1.4.0 (2026-08-23)

### 📌 Ringkasan Rilis
Pembaruan **Versi 1.4.0** menghadirkan pembaruan alur kerja **LangGraph Vector DB Search Routing** untuk konsultasi medis umum, fitur **Manajemen Ruang Poli Klinis (Clinic Room Management)** bagi Admin & Dokter, pengayaan **Knowledge Management dengan Ekstraksi File PDF & DOCX**, serta tagging kata kunci terstruktur.

---

### ✨ Fitur Baru & Peningkatan Utama

#### 1. 🔍 Alur Pencarian Vector DB Wajib pada Konsultasi Medis Umum
- **LangGraph Routing Terintegrasi**: Kueri pada mode Konsultasi Medis Umum (tanpa pemilihan pasien spesifik) sekarang **wajib melewati langkah pencarian ke Vector DB (Qdrant RAG & Evidence-Based Literature Search)** sebelum dieksekusi oleh simpul sintesis Google Gemini.
- **Audit Trail & Step Logging**: Peningkatan pencatatan langkah `Retrieval Augmentation Generation (Qdrant Vector DB)` pada `steps_executed` dan penyediaan `rag_chunks` serta `literature_summary` dalam state untuk grounding LLM yang optimal.
- **Penambahan Skenario Uji**: Penambahan pengujian skenario `test_01b_general_conversation_passes_through_vector_db_search` dan pengujian urutan eksekusi step.

#### 2. 🏥 Manajemen Ruang Poli Klinis (Clinic Room Management)
- **Modul CRUD Ruangan Poli**: Panel administrasi untuk mengelola ruangan poli (Poli Penyakit Dalam, Jantung, Bedah, Anak, Saraf, dll.) lengkap dengan kode poli, gedung, lantai, kapasitas harian, dan status aktif.
- **Penugasan Dokter & Filter Pasien**: Dokter dapat memilih ruangan poli aktif saat bertugas, dan daftar pasien akan otomatis terfilter sesuai alokasi antrean poli.
- **Endpoint API**: Penyediaan endpoint `/api/v1/admin/clinic-rooms`, `/api/v1/agent/clinic-rooms`, dan `/api/v1/agent/clinic-rooms/select`.

#### 3. 📄 Dukungan Upload Dokumen PDF & DOCX pada Knowledge Management
- **Ekstraksi Teks Otomatis**: Kemampuan mengunggah dokumen pedoman klinis dalam format `.pdf` dan `.docx` dengan ekstraksi konten teks otomatis (`pypdf` / `python-docx`).
- **Ekstraksi Kata Kunci & Metadata**: Otomatisasi pembentukan tag/keyword klinis dan pembagian dokumen menjadi chunk berukuran optimal untuk indexing Qdrant Vector DB.
- **Antarmuka Knowledge Explorer**: Penambahan komponen `FileUploader.tsx`, form modal dengan tag input interaktif, serta filter pencarian yang disempurnakan.

#### 4. 🧪 Pengujian & Verifikasi Mutu
- **40 Unit & Scenario Test Backend**: Seluruh 40 skenario pengujian backend (termasuk unit test poli dan RAG file parsing) lulus 100% (`Ran 40 tests in 59.458s - OK`).

---

## 🚀 Versi 1.3.0 (2026-08-22)

### 📌 Ringkasan Rilis
Pembaruan **Versi 1.3.0** menghadirkan peningkatan arsitektur besar pada sistem **Knowledge Management & Vector RAG (Qdrant)**, integrasi persistensi data konsultasi audio **Temp SOAP**, deteksi tanda bahaya klinis (*Clinical Red Flags*) berbasis kecerdasan buatan, serta pemutakhiran antarmuka klinis dokter (*Doctor Consultation Workspace*).

---

### ✨ Fitur Baru & Peningkatan Utama

#### 1. 🧠 Integrasi Penuh Clinical Vector RAG (Qdrant) & Initial Knowledge Base
- **Pemisahan Modul Knowledge**: Basis pengetahuan klinis awal dipisahkan ke [`backend/app/modules/rag/initial_knowledge.py`](backend/app/modules/rag/initial_knowledge.py) memuat 21 dokumen standar klinis lengkap (profil penyakit, farmakologi, interaksi obat, dan panduan praktik klinis).
- **Penghapusan Percabangan Hardcoded**: Seluruh evaluasi klinis pada skill agent telah dialihkan ke pencarian semantik vektor dinamis:
  - `node_km_disease_explanations`: Penjelasan patofisiologi dan stadium penyakit via RAG.
  - `node_diagnostic_recommendation` & `tool_generate_diagnostic_recommendations`: Rekomendasi diagnosis primer, diagnosis banding, dan kode ICD-10 via RAG.
  - `node_km_medication_recommendation` & `tool_generate_med_generation`: Rekomendasi obat lini pertama, penyesuaian dosis ginjal/hepar, kontraindikasi, dan monitoring poin via RAG.
  - `node_km_red_flag_detection` & `tool_detect_clinical_red_flags`: Deteksi ambang kegawatdaruratan dan tanda bahaya klinis via RAG.
- **Graceful Empty State**: Menangani kasus kueri kosong atau tidak ditemukan referensi tanpa menyisipkan data tiruan (*dummy data*).

#### 2. 🎙️ Persistensi Data Temp SOAP & Rekaman Audio
- **Tabel Basis Data `temp_soaps`**: Menyimpan rekaman audio, transkripsi diarization, dan struktur SOAP sementara (`Subjective`, `Objective`, `Assessment`, `Plan`, `Instruction`) sebelum dikirimkan ke SIMRS.
- **Relasi Chat Session**: Terhubung langsung dengan `chat_session_id`, `patient_id`, dan `doctor_id`.
- **Integrasi Temp SOAP pada FAQ Medis**:
  - FAQ Rekomendasi Diagnosis (FAQ 4) diperkaya dengan analisis *assessment* temp SOAP.
  - FAQ Rekomendasi Obat (FAQ 5) diperkaya dengan regimen terapi/resep temp SOAP.
  - FAQ Rencana Tindakan & Workups (FAQ 6) diperkaya dengan instruksi pemeriksaan temp SOAP.
  - FAQ Buat Draft CPPT (FAQ 10) memuat draf langsung dari data temp SOAP audio.

#### 3. 🚨 Deteksi Tanda Bahaya Klinis & Kriteria Kegawatdaruratan (Clinical Red Flags)
- **Parameter Deteksi Terstruktur**: Mem-parse nama alert, tingkat keparahan (*Severity: Critical / High*), kriteria pemicu (*trigger criteria*), dan tindakan darurat (*emergency action*).
- **Panduan Triase Darurat**: Memberikan rekomendasi rujukan segera ke IGD / ICU jika ditemukan tanda instabilitas klinis.

#### 4. 🎨 Pembaruan Antarmuka & Editor CPPT/SOAP
- **Panel Interaktif Template Plan**: Panel akordion buka-tutup pada `CPPTEditorModal.tsx` untuk memilih template umum dan input kustom dokter.
- **Multi-Tab Draft RME Modal**: Integrasi tab Anamnesis, Diagnosis, Resep Obat, dan CPPT S/O/A/P dengan tombol sinkronisasi ke SIMRS.

#### 5. 🧪 Pengujian & Verifikasi Mutu
- **39 Unit Test Backend**: Seluruh skenario pengujian klinis, RAG retrieval, dan guardrails keselamatan berhasil lulus 100% (`Ran 39 tests in 52.939s - OK`).

---

## 📜 Riwayat Versi Sebelumnya

### Versi 1.2.0 (2026-08-20)
- Integrasi **Model Context Protocol (MCP)** untuk SIMRS Bridge.
- Implementasi sistem validasi keluaran LLM (*LLM Output Guardrails & Safety Validator*).
- Transkripsi konsultasi audio dokter-pasien via Google Gemini STT.

### Versi 1.1.0 (2026-08-15)
- Alur penalaran *Multi-step reasoning* menggunakan **LangGraph**.
- Checkpoint persistence dengan SQLite Checkpointer.
- Streaming respons real-time (Server-Sent Events) ke antarmuka dokter.

### Versi 1.0.0 (2026-08-01)
- Rilis inisial platform AssistanMedixa (AIMedical).
- Modul autentikasi JWT dan Role-Based Access Control (RBAC).
- Integrasi Google Gemini 2.0 Flash untuk asisten klinis dasar.
