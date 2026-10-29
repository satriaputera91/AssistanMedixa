# 🩺 AssistanMedixa (AssistantMedixa)

<div align="center">

[![FastAPI](https://img.shields.io/badge/FastAPI-0.141+-009688.svg?style=for-the-badge&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-Agentic_Workflow-FF6F00.svg?style=for-the-badge&logo=LangChain&logoColor=white)](https://langchain-ai.github.io/langgraph/)
[![Generative AI](https://img.shields.io/badge/Generative_AI-Agentic_LLM-4285F4.svg?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev/)
[![Qdrant](https://img.shields.io/badge/Qdrant-Vector_RAG-DC2626.svg?style=for-the-badge&logo=qdrant&logoColor=white)](https://qdrant.tech/)
[![Next.js](https://img.shields.io/badge/Next.js-14_App_Router-000000.svg?style=for-the-badge&logo=nextdotjs&logoColor=white)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.5+-3178C6.svg?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Version](https://img.shields.io/badge/Release-v1.4.0-blue.svg?style=for-the-badge)](VERSION_NOTES.md)
[![License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](LICENSE)

**Platform Asisten Klinis AI Berbasis Agentic Architecture (FastAPI, LangGraph, Model Context Protocol & Generative AI)**

[Fitur Utama](#-fitur-utama) •
[Arsitektur Sistem](#-arsitektur-sistem) •
[Struktur Direktori](#-struktur-direktori) •
[Instalasi & Penggunaan](#-instalasi--penggunaan) •
[API Reference](#-api-reference) •
[Version Notes](VERSION_NOTES.md) •
[Disclaimer Medis](#-disclaimer-medis)

</div>

---

## 📖 Ringkasan Proyek

**AssistanMedixa (AssistantMedixa)** adalah platform kecerdasan buatan klinis (*Clinical Decision Support System*) yang dirancang untuk membantu tenaga medis (dokter dan staf klinis) dalam mempercepat alur konsultasi pasien, pembuatan rekam medis CPPT/SOAP, analisis anamnesis terstruktur, hingga pengecekan keselamatan resep obat.

Sistem dibangun dengan arsitektur **Modular Monolith** berkinerja tinggi, mengintegrasikan alur penalaran bertingkat (*multi-step reasoning*) menggunakan **LangGraph**, protokol standar **Model Context Protocol (MCP)** untuk integrasi data SIMRS (Sistem Informasi Manajemen Rumah Sakit), dan **RAG (Retrieval-Augmented Generation)** berbasis Qdrant Vector DB dengan Generative AI.

---

## ✨ Fitur Utama

- 🧠 **Autonomous Medical Agent (LangGraph)**
  - State machine workflow terstruktur: Anamnesis → Differential Diagnosis → SOAP/CPPT Generation → Medication Recommendation → Red Flags Detection → Safety Guardrail Verification.
  - Alur **Pencarian Vector DB Wajib**: Setiap konsultasi medis umum secara otomatis melewati tahap pencarian semantik vektor Qdrant & Evidence-Based Literature sebelum sintesis respons.
  - Streaming respons real-time (Server-Sent Events) dengan visualisasi langkah penalaran AI.
- 🔌 **Model Context Protocol (MCP) untuk SIMRS**
  - Standardized tool integration untuk membaca riwayat rekam medis (EMR), hasil laboratorium, alergi obat, dan stok farmasi rumah sakit.
- 📚 **Clinical Knowledge Vector RAG Engine (Qdrant) & Dokumen PDF/DOCX**
  - Mesin pencarian semantik panduan praktik klinis (PPK), formularium nasional, diagnosis kerja, dan basis pengetahuan interaksi obat menggunakan **Qdrant Vector DB** dan **Generative AI Embeddings**.
  - Dukungan unggah berkas dokumen `.pdf` dan `.docx` dengan ekstraksi teks, pembentukan kata kunci otomatis, dan chunking dokumen ke Vector DB.
- 🏥 **Manajemen Ruang Poli Klinis (Clinic Room Management)**
  - Panel administrasi untuk mengelola ruangan poli (Penyakit Dalam, Jantung, Bedah, Anak, dll.) lengkap dengan kapasitas antrean harian dan status aktif.
  - Integrasi penugasan dokter jaga dan penyaringan daftar pasien aktif berdasarkan poli terpilih.
- 🎙️ **Multimodal Audio Consultation & Temp SOAP Storage**
  - Transkripsi dan ekstraksi poin penting konsultasi verbal dokter-pasien secara instan menggunakan Generative AI Multimodal.
  - Penyimpanan terstruktur SOAP sementara (`temp_soaps`) pada basis data relasional sebelum dikonfirmasi dan dikirimkan ke SIMRS.
  - Pengayaan otomatis FAQ Medis (Diagnosis, Rekomendasi Obat, Workups/Tindakan) dengan data analisis rekaman audio / SOAP sementara.
- 🚨 **Clinical Red Flags & Emergency Triage**
  - Deteksi dini kondisi gawat darurat dan ambang kegawatdaruratan (*red flags*) secara dinamis dengan klasifikasi keparahan (*Critical / High*).
- 🛡️ **Medical Safety Guardrails & Moderation**
  - Validasi kontraindikasi obat, dosis batas aman terhadap fungsi ginjal (eGFR), dan deteksi alergi pasien.
- 📊 **Panel Administrasi & Audit Trail**
  - Dashboard pemantauan analitik konsultasi, manajemen pengguna (Dokter, Admin, Farmasi), log audit riwayat akses, dan konfigurasi guardrails.
- 🎨 **Modern & Intuitive Clinical UI**
  - Antarmuka responsif berbasis Next.js 14 App Router, Tailwind CSS, Dark/Light theme, panel akordion template Plan, dan modal multi-tab draf RME (Anamnesis, Diagnosis, Resep Obat, CPPT).


---

## 🏛️ Arsitektur Sistem

```mermaid
flowchart TD
    subgraph Client ["Frontend (Next.js 14 + Tailwind)"]
        UI[Doctor Consultation UI & SOAP Editor]
        AdminUI[Admin Dashboard & Knowledge Management]
        AudioRec[Audio Recording & STT Module]
    end

    subgraph Backend ["Backend (FastAPI Modular Monolith)"]
        API[API Gateway / Router]
        Auth[Auth & RBAC Module - JWT]
        Guardrails[Medical Guardrails Engine]
        
        subgraph AgenticCore ["LangGraph Agent Engine"]
            StateGraph[LangGraph State Machine]
            AnamnesisNode[Anamnesis Node]
            DiagnosisNode[Diagnosis Node]
            SOAPNode[SOAP / CPPT Node]
            PrescriptionNode[Prescription Node]
            SafetyNode[Safety Check Node]
        end

        subgraph Integrations ["Integration Layers"]
            MCP[MCP Server & Client - SIMRS Integration]
            RAG[RAG Service - Generative AI Embeddings]
        end
    end

    subgraph External ["External Services & Storage"]
        GenAI[Generative AI API]
        Qdrant[(Qdrant Vector DB)]
        SQLite[(SQLite Checkpoint DB)]
        SIMRS[(SIMRS / Hospital Database)]
    end

    UI -->|REST / SSE| API
    AdminUI -->|REST API| API
    AudioRec -->|Audio Multipart| API

    API --> Auth
    API --> AgenticCore
    API --> Guardrails
    
    StateGraph --> AnamnesisNode --> DiagnosisNode --> SOAPNode --> PrescriptionNode --> SafetyNode
    AgenticCore --> GenAI
    AgenticCore --> SQLite
    AgenticCore --> MCP
    AgenticCore --> RAG

    MCP --> SIMRS
    RAG --> Qdrant
    RAG --> GenAI
```

---

## 📂 Struktur Direktori

```text
AssistanMedixa/
├── backend/
│   ├── app/
│   │   ├── core/                  # Konfigurasi aplikasi, database, security, & LLM fallback
│   │   │   ├── config.py
│   │   │   ├── database.py        # Persistence & database models
│   │   │   ├── llm_fallback.py    # Automatic Gemini LLM & STT fallback chain
│   │   │   └── security.py
│   │   ├── modules/               # Domain modules (Modular Monolith)
│   │   │   ├── admin/             # Dashboard admin, user management, & analytics
│   │   │   ├── auth/              # JWT authentication & authorization
│   │   │   ├── chat/              # Chat session management & Audio STT
│   │   │   ├── guardrails/        # Safety verification & clinical rules
│   │   │   ├── mcp/               # Model Context Protocol (SIMRS & SATUSEHAT Server/Client)
│   │   │   ├── medical_agent/     # LangGraph Agent Graph, skills, state, & clinical tools
│   │   │   └── rag/               # Vector search, initial knowledge base, & Qdrant service
│   │   │       ├── initial_knowledge.py  # 21 Clinical reference knowledge documents
│   │   │       └── rag_service.py        # Dedicated Qdrant RAG service
│   │   └── main.py                # FastAPI entry point & middleware
│   ├── tests/                     # Automated test suites
│   ├── Dockerfile                 # Dockerfile untuk Backend FastAPI (Port 3038)
│   ├── run.sh                     # Backend launch script
│   └── .env.example               # Template environment variable backend
│
├── frontend/
│   ├── app/                       # Next.js 14 App Router
│   │   ├── admin/                 # Admin Dashboard Pages
│   │   ├── doctor/                # Doctor Consultation Workspace
│   │   ├── knowledge/             # Knowledge Management & RAG Explorer
│   │   ├── login/                 # Authentication Page
│   │   ├── layout.tsx             # Root layout & Theme provider
│   │   └── page.tsx               # Landing & Redirects
│   ├── components/                # Reusable UI Components
│   │   ├── admin/                 # Admin charts, audit feeds, user tables, clinic room management
│   │   ├── chat/                  # Chat window, SOAP/CPPT editor, Audio recorder, Draft RME
│   │   ├── common/                # Navbar, modals, metrics card
│   │   └── knowledge/             # Document uploader (PDF/DOCX), table & search explorer
│   ├── hooks/                     # Custom React Hooks
│   ├── services/                  # API Client Services
│   ├── Dockerfile                 # Dockerfile untuk Frontend Next.js (Port 8086)
│   ├── next.config.js             # Konfigurasi Next.js & proxy API rewrites
│   ├── tailwind.config.js         # Tailwind styling configuration
│   └── package.json               # Frontend dependencies & scripts
│
├── docker/
│   └── mongodb/
│       └── init-mongo.sh          # Script inisialisasi user & database MongoDB
├── docker-compose.yml             # Orkestrasi Docker Compose (MongoDB, Backend, Frontend)
├── .dockerignore                  # Docker build context ignore rules
├── .gitignore                     # Git ignore rules
├── requirements.txt               # Python backend dependencies
├── VERSION_NOTES.md               # Catatan rilis dan riwayat versi
└── README.md                      # Dokumentasi teknis proyek
```

---

## 🚀 Instalasi & Penggunaan

### 📋 Prasyarat Sistem
- **Docker & Docker Compose** *(Direkomendasikan untuk menjalankan seluruh stack)*
- **Python**: Versi `3.10` atau lebih baru *(untuk instalasi manual)*
- **Node.js**: Versi `18.x` atau `20.x` disertai `pnpm` / `npm` *(untuk instalasi manual)*
- **Google Gemini API Key**: Dapatkan dari [Google AI Studio](https://aistudio.google.com/)

---

### 🐳 Opsi A: Menjalankan dengan Docker Compose (Direkomendasikan)

Seluruh layanan (**MongoDB**, **Backend FastAPI**, dan **Frontend Next.js**) telah dikonfigurasi di dalam `docker-compose.yml`.

1. **Pastikan file `backend/.env` sudah dikonfigurasi:**
   ```bash
   cp backend/.env.example backend/.env
   ```
   Sesuaikan `GEMINI_API_KEY`, kredensial SatuSehat (`SS_*`), serta konfigurasi MongoDB (`MONGODB_*`) di `backend/.env`:
   ```env
   GEMINI_MODEL_NAME=gemini-3.8-flash
   GEMINI_STT_MODEL_NAME=gemini-3.8-flash
   GEMINI_FALLBACK_MODELS=gemini-3.5-flash-lite,gemini-3.7-flash,gemini-3.6-flash,gemini-3.5-flash,gemini-3.1-flash-lite,gemini-flash-latest,gemini-flash-lite-latest

   MONGODB_HOST=localhost
   MONGODB_PORT=27017
   MONGODB_USER=medixa
   MONGODB_PASSWORD=admin2026
   MONGODB_DATABASE=assistant_medixa
   MONGODB_AUTH_SOURCE=assistant_medixa
   ```

2. **Jalankan seluruh container (MongoDB + Backend + Frontend):**
   ```bash
   docker-compose --env-file ./backend/.env up -d --build
   ```
   Atau jika hanya ingin menjalankan container **MongoDB** saja:
   ```bash
   docker-compose --env-file ./backend/.env up -d mongodb
   ```

3. **Akses Layanan:**
   | Layanan | Container Name | Port | URL / Endpoint |
   | :--- | :--- | :--- | :--- |
   | **Frontend Web UI** | `aimedical-frontend` | `8086` | `http://localhost:8086` |
   | **Backend API** | `aimedical-backend` | `3038` | `http://localhost:3038` |
   | **Swagger API Docs** | `aimedical-backend` | `3038` | `http://localhost:3038/docs` |
   | **MongoDB** | `aimedical-mongodb` | `27017` | `mongodb://medixa:admin2026@localhost:27017/assistant_medixa?authSource=assistant_medixa` |

4. **Perintah Berguna Docker Compose:**
   ```bash
   # Melihat status container
   docker-compose ps

   # Melihat log layanan secara real-time
   docker-compose logs -f backend frontend mongodb

   # Menghentikan seluruh layanan
   docker-compose down
   ```

---

### 💻 Opsi B: Menjalankan Secara Manual (Local Development)

#### 1️⃣ Konfigurasi Backend (Port `3038`)

1. **Buat dan aktifkan Virtual Environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate   # Di Windows: .venv\Scripts\activate
   ```

2. **Instal dependensi Python:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Konfigurasi Environment Variables:**
   Salin template `.env.example` ke `backend/.env` dan isi kredensial yang sesuai:
   ```bash
   cp backend/.env.example backend/.env
   ```
   *Pastikan mengisi nilai `GEMINI_API_KEY` dan `SECRET_KEY`.*

4. **Jalankan Backend Server:**
   ```bash
   cd backend
   uvicorn app.main:app --host 0.0.0.0 --port 3038 --reload
   ```
   *Swagger API Documentation akan tersedia di `http://localhost:3038/docs`.*

#### 2️⃣ Konfigurasi Frontend (Port `8086`)

1. **Pindah ke direktori frontend:**
   ```bash
   cd frontend
   ```

2. **Pastikan `frontend/.env` mengarah ke port Backend (`3038`):**
   ```env
   NEXT_PUBLIC_BACKEND_URL=http://localhost:3038
   ```

3. **Instal dependensi Node.js:**
   ```bash
   pnpm install
   # atau menggunakan npm
   npm install
   ```

4. **Jalankan Frontend Development Server pada Port `8086`:**
   ```bash
   pnpm run dev -- -p 8086
   ```
   *Aplikasi web akan dapat diakses di `http://localhost:8086`.*

---

## 📡 API Reference Ringkas

| Modul | Method | Endpoint | Deskripsi |
| :--- | :--- | :--- | :--- |
| **Auth** | `POST` | `/api/v1/auth/login` | Otentikasi dan penerbitan JWT Access Token |
| **Auth** | `GET` | `/api/v1/auth/me` | Informasi profil pengguna yang sedang login |
| **Medical Agent** | `POST` | `/api/v1/agent/chat` | Eksekusi penalaran LangGraph Medical Agent |
| **Medical Agent** | `POST` | `/api/v1/agent/chat/stream` | Stream real-time respons & reasoning steps |
| **Poli / Clinic Rooms** | `GET` / `POST` | `/api/v1/admin/clinic-rooms` | CRUD manajemen ruangan poli klinis |
| **Poli / Clinic Rooms** | `POST` | `/api/v1/agent/clinic-rooms/select` | Pemilihan ruangan poli aktif dokter |
| **Chat & STT** | `POST` | `/api/v1/agent/chat/audio` | Transkripsi audio konsultasi dokter & SOAP Temp via Generative AI STT |
| **RAG & Knowledge** | `POST` | `/api/v1/rag/search` | Pencarian pedoman klinis & literatur obat |
| **RAG & Knowledge** | `POST` | `/api/v1/rag/upload-file` | Ekstraksi & indexing dokumen pedoman klinis (PDF/DOCX) |
| **MCP SIMRS** | `POST` | `/api/v1/mcp/execute` | Eksekusi tool pemanggilan data SIMRS |
| **Guardrails** | `POST` | `/api/v1/guardrails/verify` | Evaluasi kepatuhan keselamatan klinis |
| **Health** | `GET` | `/api/health` | Healthcheck status backend dan AI service |

---

## 🛡️ Standar Keamanan & Best Practices

- 🔐 **JWT Token Authentication**: Seluruh rute terproteksi diverifikasi dengan JWT token dan RBAC (*Role-Based Access Control*).
- 🛡️ **Medical Verification Layer**: Hasil rekomendasi AI diformulasikan sebagai *Clinical Support System* dengan konfirmasi akhir berada pada dokter penanggung jawab.
- 🗄️ **Persistent State Checkpoints**: Riwayat sesi penalaran LangGraph tersimpan aman dan terisolasi per sesi konsultasi.
- 🔒 **Environment Security**: Tidak ada *hardcoded secrets* maupun kunci API dalam basis kode.

---

## ⚠️ Disclaimer Medis

> **PENTING:**
> **AssistanMedixa** dikembangkan sebagai perangkat lunak pembantu keputusan klinis (*Clinical Decision Support System / CDSS*). Sistem ini **bukan pengganti penilaian klinis langsung, diagnosis resmi, maupun keputusan independen dokter berlisensi**. Semua rekomendasi diagnosis, tindakan medis, dan terapi obat wajib ditinjau dan divalidasi kembali oleh tenaga medis yang berwenang sebelum diterapkan kepada pasien.

---

## 📄 Lisensi

Didistribusikan di bawah Lisensi MIT. Lihat file `LICENSE` untuk informasi lebih lanjut.

---

<div align="center">
  <sub>Dibangun dengan dedikasi untuk memajukan integrasi AI dalam dunia medis & kesehatan.</sub>
</div>
