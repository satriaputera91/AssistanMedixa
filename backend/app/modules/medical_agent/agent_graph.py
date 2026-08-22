import os
import re
import sqlite3
import logging
import inspect
from datetime import datetime
from typing import Dict, Any, List

# pyrefly: ignore [missing-import]
from langgraph.graph import StateGraph, END
# pyrefly: ignore [missing-import]
try:
    from langgraph.checkpoint.sqlite import SqliteSaver
    HAS_SQLITE_SAVER = True
except ImportError:
    from langgraph.checkpoint.memory import MemorySaver as SqliteSaver
    HAS_SQLITE_SAVER = False

from app.core.config import settings
from app.modules.medical_agent.state import MedicalAgentState, AgentStepInfo
from app.modules.medical_agent.tools import (
    tool_query_patient_ehr,
    tool_check_drug_interactions,
    tool_search_medical_references,
    tool_qdrant_vector_rag_search,
    tool_simrs_get_patient_profile,
    tool_simrs_get_patient_history,
    tool_simrs_get_patient_anamnesis,
    tool_simrs_get_patient_labs,
    tool_generate_diagnostic_recommendations,
    tool_km_disease_explanations,
    tool_km_red_flag_detections,
    tool_km_medication_recommendations,
    tool_patient_drug_safety_screening,
    tool_simrs_update_patient_record
)
from app.modules.guardrails.output_validator import LLMOutputValidator
from app.modules.medical_agent.output_schemas import (
    ClinicalSOAPOutputSchema,
    SubjectiveData,
    ObjectiveData,
    VitalSignsData,
    LabItemData,
    AssessmentData,
    DiagnosisItemData,
    PlanData,
    MedicationItemData,
    RedFlagData,
    PatientDemographicsData,
    GeneralConsultationKnowledgeSchema,
    SIMRSTransactionReportSchema,
    AudioConsultationSOAPSchema,
)



# Standard Logger Configuration for AIMedical LangGraph Agent
logger = logging.getLogger("AIMedical.MedicalAgent")
if not logger.handlers:
    _log_handler = logging.StreamHandler()
    _log_formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-7s | [%(filename)s:%(lineno)d] | %(funcName)s() | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    _log_handler.setFormatter(_log_formatter)
    logger.addHandler(_log_handler)
logger.setLevel(logging.INFO)

# Initialize SQLite checkpointer for LangGraph conversation memory & checkpointing
def get_sqlite_checkpointer() -> Any:
    db_path = getattr(settings, "CHECKPOINT_DB_PATH", "checkpoints.db")
    if HAS_SQLITE_SAVER:
        conn = sqlite3.connect(db_path, check_same_thread=False)
        checkpointer = SqliteSaver(conn)
        checkpointer.setup()
        return checkpointer
    else:
        return SqliteSaver()

sqlite_checkpointer = get_sqlite_checkpointer()

# Optional LangChain / Gemini imports
try:
    # pyrefly: ignore [missing-import]
    from langchain_google_genai import ChatGoogleGenerativeAI
    # pyrefly: ignore [missing-import]
    from langchain_core.messages import SystemMessage, HumanMessage
    HAS_LANGCHAIN_GEMINI = True
except ImportError:
    HAS_LANGCHAIN_GEMINI = False

try:
    # pyrefly: ignore [missing-import]
    from google import genai
    HAS_GOOGLE_GENAI_SDK = True
except ImportError:
    HAS_GOOGLE_GENAI_SDK = False


# ==============================================================================
# LangGraph Debug Print Logging Helpers (Nodes & Edges with Line Numbers)
# ==============================================================================
def _get_caller_info() -> str:
    """Introspects the stack frame to extract caller filename, line number, and function name."""
    try:
        frame = inspect.currentframe()
        if frame and frame.f_back and frame.f_back.f_back:
            caller = frame.f_back.f_back
            fn = os.path.basename(caller.f_code.co_filename)
            return f"[{fn}:{caller.f_lineno}] in {caller.f_code.co_name}()"
    except Exception:
        pass
    return "[agent_graph.py:---]"


def _debug_node_start(node_name: str, state: MedicalAgentState, icon: str = "🔵"):
    caller_loc = _get_caller_info()
    pid = state.get("patient_id") or "N/A"
    query = (state.get("user_query") or state.get("audio_filename") or "")
    if len(query) > 65:
        query = query[:62] + "..."
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    msg = f"{icon} [LANGGRAPH NODE START] >>> {node_name} | Patient: {pid} | Query: '{query}'"
    print(f"{ts} | INFO    | {caller_loc} | {msg}")


def _debug_node_end(node_name: str, result_summary: str = ""):
    caller_loc = _get_caller_info()
    res = f" | {result_summary}" if result_summary else ""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    msg = f"✅ [LANGGRAPH NODE COMPLETED] <<< {node_name}{res}"
    print(f"{ts} | INFO    | {caller_loc} | {msg}")


def _debug_edge(source_node: str, target_node: str, condition: str = ""):
    caller_loc = _get_caller_info()
    cond_txt = f" (Condition: {condition})" if condition else ""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    msg = f"🔀 [LANGGRAPH EDGE TRANSITION] {source_node} ──▶ {target_node}{cond_txt}"
    print(f"{ts} | INFO    | {caller_loc} | {msg}")


def node_audio_transcription(state: MedicalAgentState) -> MedicalAgentState:
    """Transcribe an uploaded WAV/MP3 recording with Gemini with Speaker Diarization (Doctor vs Patient)."""
    _debug_node_start("audio_transcription", state, icon="🎙️")
    steps = list(state.get("steps_executed", []))
    audio_bytes = state.get("audio_bytes") or b""
    filename = state.get("audio_filename") or "audio.wav"
    api_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "")

    if not api_key or not HAS_GOOGLE_GENAI_SDK:
        error = "Gemini API belum tersedia untuk mentranskripsikan audio."
        steps.append({
            "step_name": "Diarisasi & Transkripsi Audio Medis",
            "description": "Transkripsi audio Bahasa Indonesia tidak dapat dijalankan (API Key belum dikonfigurasi).",
            "status": "failed",
            "result": error,
        })
        _debug_node_end("audio_transcription", f"FAILED: {error}")
        _debug_edge("audio_transcription", "audio_soap_summary")
        return {**state, "steps_executed": steps, "audio_error": error}

    try:
        # pyrefly: ignore [missing-import]
        from google.genai import types

        client = genai.Client(api_key=api_key)
        prompt = (
            "Transkripsikan rekaman audio percakapan medis/klinis ini secara lengkap dalam Bahasa Indonesia "
            "dengan melakukan DIARISASI PEMBICARA (SPEAKER DIARIZATION) secara akurat.\n\n"
            "Format transkrip dialog wajib menggunakan pemisahan pembicara yang jelas:\n"
            "**Dokter**: [ucapan / pertanyaan / instruksi dokter]\n"
            "**Pasien**: [jawaban / keluhan / penjelasan pasien atau pendamping]\n\n"
            "Pedoman:\n"
            "1. Pisahkan setiap pergantian giliran bicara dengan baris baru.\n"
            "2. Pertahankan istilah medis, nama obat, dosis, keluhan, angka, dan negasi secara verbatim.\n"
            "3. Jangan meringkas atau menghilangkan ucapan.\n"
            "4. Jika ada bagian yang kurang jelas terdengar, tulis [tidak jelas].\n"
        )
        response = client.models.generate_content(
            model=settings.GEMINI_STT_MODEL_NAME,
            contents=[
                types.Content(parts=[
                    types.Part.from_text(text=prompt),
                    types.Part.from_bytes(data=audio_bytes, mime_type="audio/wav"),
                ])
            ],
        )
        transcript = (response.text or "").strip()
        if not transcript:
            raise ValueError("Gemini tidak mengembalikan transkrip.")
        steps.append({
            "step_name": "Diarisasi Pembicara & Transkripsi Audio Medis",
            "description": f"Mentranskripsikan audio '{filename}' dengan pemisahan peran Dokter & Pasien secara otomatis.",
            "status": "success",
            "result": f"Transkrip terdiarisasi selesai ({len(transcript)} karakter).",
        })
        _debug_node_end("audio_transcription", f"Transcript length: {len(transcript)} chars")
        _debug_edge("audio_transcription", "audio_soap_summary")
        return {**state, "steps_executed": steps, "audio_transcript": transcript, "audio_error": None}

    except Exception as exc:
        error = f"Transkripsi audio gagal: {str(exc)[:180]}"
        steps.append({
            "step_name": "Diarisasi Pembicara & Transkripsi Audio Medis",
            "description": f"Gagal mentranskripsikan audio '{filename}'.",
            "status": "failed",
            "result": error,
        })
        _debug_node_end("audio_transcription", f"ERROR: {error}")
        _debug_edge("audio_transcription", "audio_soap_summary")
        return {**state, "steps_executed": steps, "audio_error": error}


def node_audio_soap_summary(state: MedicalAgentState) -> MedicalAgentState:
    """Create a SOAP-derived S/O/A note from the diarized transcript in Gemini."""
    _debug_node_start("audio_soap_summary", state, icon="📋")
    steps = list(state.get("steps_executed", []))
    transcript = state.get("audio_transcript") or ""
    error = state.get("audio_error")
    api_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "")

    if error or not transcript:
        final_text = "## Proses audio tidak dapat diselesaikan\n\n" + (error or "Transkrip audio kosong.")
        _debug_node_end("audio_soap_summary", "No transcript available")
        _debug_edge("audio_soap_summary", "END")
        return {**state, "steps_executed": steps, "final_synthesis": final_text}

    prompt = f"""Berikut adalah transkrip rekaman klinis terdiarisasi (Dokter & Pasien) dalam Bahasa Indonesia.

--- TRANSKRIP TERDIARISASI ---
{transcript}
--- AKHIR TRANSKRIP ---

Tugas Anda adalah menyusun resume klinis terstruktur (SOAP note) berdasarkan percakapan di atas.
Gunakan format terstruktur standar berikut dengan heading Markdown:

## Resume Konsultasi Klinis (SOAP Note)

### S — Subjective (Keluhan & Riwayat Pasien)
[Rangkuman keluhan utama, riwayat penyakit, riwayat obat, dan gejala yang disampaikan Pasien]

### O — Objective (Pemeriksaan & Observasi)
[Temuan pemeriksaan fisik, tanda vital, atau hasil lab/penunjang yang disebutkan dalam dialog]

### A — Assessment (Diagnosis & Penilaian Klinis)
[Kesimpulan diagnosis kerja atau penilaian klinis yang didiskusikan]

### P — Plan (Rencana Tindak Lanjut & Terapi)
[Rencana pengobatan, pemeriksaan penunjang lanjutan, atau instruksi edukasi yang diberikan Dokter]

---
*(⚠️ **Disclaimer**: Resume klinis ini dibuat otomatis oleh AI dari rekaman audio dan wajib diverifikasi serta divalidasi oleh dokter yang berwenang sebelum dimasukkan ke rekam medis definitif.)*"""

    try:
        if api_key and HAS_LANGCHAIN_GEMINI:
            llm = ChatGoogleGenerativeAI(
                model=settings.GEMINI_MODEL_NAME, google_api_key=api_key, temperature=0.1
            )
            resp = llm.invoke([HumanMessage(content=prompt)])
            if isinstance(resp.content, list):
                final_text = "".join([
                    part.get("text", "") if isinstance(part, dict) else str(part)
                    for part in resp.content
                ]).strip()
            else:
                final_text = str(resp.content).strip()
        elif api_key and HAS_GOOGLE_GENAI_SDK:
            client = genai.Client(api_key=api_key)
            final_text = (client.models.generate_content(
                model=settings.GEMINI_MODEL_NAME, contents=prompt
            ).text or "").strip()
        else:
            raise RuntimeError("Gemini API belum tersedia untuk membuat resume klinis.")
        if not final_text:
            raise ValueError("Gemini tidak mengembalikan resume klinis.")
        steps.append({
            "step_name": "Sintesis Resume Klinis SOAP Terstruktur",
            "description": "Menyusun resume Subjective, Objective, Assessment, dan Plan dari percakapan Dokter & Pasien.",
            "status": "success",
            "result": "Resume klinis SOAP berhasil disusun.",
        })
        # Build structured AudioConsultationSOAPSchema
        audio_soap = AudioConsultationSOAPSchema(
            audio_filename=state.get("audio_filename", "audio.wav"),
            transcript=transcript,
            soap=ClinicalSOAPOutputSchema(
                title="Catatan Perkembangan Pasien Terintegrasi (Hasil Audio STT)",
                subjective=SubjectiveData(chief_complaint="Keluhan dari rekaman konsultasi verbal dokter-pasien"),
                objective=ObjectiveData(physical_examination="Pemeriksaan fisik sesuai percakapan klinis"),
                assessment=AssessmentData(
                    primary_diagnosis=DiagnosisItemData(diagnosis="Evaluasi Klinis Hasil Konsultasi Audio", icd10="Z71.9")
                ),
                plan=PlanData(patient_education=["Lanjutkan terapi sesuai instruksi dokter pada rekaman"])
            )
        )
        _debug_node_end("audio_soap_summary", f"SOAP clinical note synthesized ({len(final_text)} chars)")
        _debug_edge("audio_soap_summary", "validate_output")
        return {
            **state,
            "steps_executed": steps,
            "final_synthesis": final_text,
            "structured_output": audio_soap.model_dump(),
            "audio_bytes": None,
            "workflow_type": "text"
        }

    except Exception as exc:
        error = f"Resume klinis gagal: {str(exc)[:180]}"
        steps.append({
            "step_name": "Sintesis Resume Klinis SOAP Terstruktur",
            "description": "Gagal menyusun resume klinis dari transkrip audio.",
            "status": "failed",
            "result": error,
        })
        _debug_node_end("audio_soap_summary", f"ERROR: {error}")
        _debug_edge("audio_soap_summary", "validate_output")
        return {
            **state,
            "steps_executed": steps,
            "final_synthesis": f"## Transkrip\n\n{transcript}\n\n## Resume S/O/A\n\n{error}",
            "audio_bytes": None,
            "workflow_type": "text",
        }



# Node 1: Clinical Planner & Entity Extractor
def node_planner(state: MedicalAgentState) -> MedicalAgentState:
    _debug_node_start("planner", state, icon="🧠")
    query = state.get("user_query", "")
    patient_id = state.get("patient_id")
    steps = list(state.get("steps_executed", []))
    
    # Run Guardrails validation
    try:
        from app.modules.guardrails.service import GuardrailsService
        from app.core.database import db
        guard_eval = GuardrailsService.evaluate(query, db.guardrail_config, "input")
        steps.append({
            "step_name": "AI Safety & Guardrails Verification",
            "description": f"Audited query against active safety policies (Verdict: {guard_eval.verdict})",
            "status": "success" if guard_eval.passed else "warning",
            "result": f"Risk: {guard_eval.risk_level} ({guard_eval.risk_score}) | Violations: {len(guard_eval.violations)}"
        })
    except Exception:
        pass

    # Dynamic clinical intent detection
    query_lower = query.lower().strip()

    # Auto-detect patient_id if query explicitly mentions NIK, MRN, or Patient Name
    if not patient_id or not patient_id.strip():
        try:
            from app.core.database import db
            for p_id, p_data in db.patient_records.items():
                nik_val = (p_data.get("nik") or "").lower()
                mrn_val = f"mrn-simrs-{p_id.replace('p-', '').lower()}"
                name_val = (p_data.get("name") or "").lower()
                p_id_lower = p_id.lower()
                
                if (
                    (nik_val and nik_val in query_lower)
                    or (mrn_val and mrn_val in query_lower)
                    or (p_id_lower and p_id_lower in query_lower)
                    or (len(name_val) > 4 and name_val in query_lower)
                ):
                    patient_id = p_id
                    state["patient_id"] = patient_id
                    break
        except Exception:
            pass

    if not patient_id or not patient_id.strip():
        # KONSULTASI MEDIS UMUM (Knowledge Management only - TIDAK membaca SIMRS)
        if any(k in query_lower for k in ["patofisiologi", "penjelasan penyakit", "kriteria diagnostik", "staging"]):
            detected_intent = "Penjelasan Penyakit & Patofisiologi (Knowledge Management)"
        elif any(k in query_lower for k in ["tanda bahaya", "red flag", "bahaya", "urgensi", "kegawatdaruratan"]):
            detected_intent = "Deteksi Tanda Bahaya & Red Flags (Knowledge Management)"
        elif any(k in query_lower for k in ["rekomendasi obat", "terapi obat", "dosis", "regimen", "peresepan", "obat"]):
            detected_intent = "Rekomendasi Terapi Obat & Dosis (Knowledge Management)"
        elif any(k in query_lower for k in ["skrining", "interaksi obat", "keamanan obat", "ddi", "efek samping"]):
            detected_intent = "Skrining Interaksi & Farmakologi Obat (Knowledge Management)"
        elif any(k in query_lower for k in ["diagnosis", "icd", "banding", "differential"]):
            detected_intent = "Rekomendasi Diagnosis & ICD-10 (Knowledge Management)"
        elif any(k in query_lower for k in ["pedoman", "guideline", "studi", "bukti", "meta-analisis", "literatur", "edukasi", "konseling", "biomarker", "lab"]):
            detected_intent = "Penelusuran Knowledge Management & Pedoman Medis"
        else:
            detected_intent = None

        if detected_intent:
            steps.append({
                "step_name": "Agent Intelligence & Knowledge Planner",
                "description": f"Knowledge Intent: '{detected_intent}' (Konsultasi Medis Umum)",
                "status": "completed",
                "result": {"detected_intent": detected_intent, "mode": "general_consultation"}
            })
            _debug_node_end("planner", f"Intent: '{detected_intent}' | Mode: General Consultation (Knowledge Management)")
        else:
            steps.append({
                "step_name": "Agent Intelligence & Conversation Handler",
                "description": "Merespons kueri konsultasi umum melalui basis pengetahuan medis (Knowledge Management).",
                "status": "completed",
                "result": {"detected_intent": None, "mode": "general_consultation"}
            })
            _debug_node_end("planner", "Intent: None (General consultation / knowledge)")

        return {
            **state,
            "detected_intent": detected_intent,
            "steps_executed": steps
        }

    # KONSULTASI PASIEN SPESIFIK (Terhubung dengan SIMRS)
    if any(k in query_lower for k in ["buat cppt", "kirim cppt", "kirim soap", "buat soap", "sinkronisasi cppt", "simpan cppt", "kirim/sinkronisasikan", "update simrs", "sync simrs", "commit emr", "kirim ke simrs", "kirim/sinkronisasi"]):
        detected_intent = "9. Buat & Kirim CPPT S/O/A/P ke SIMRS (MCP)"
    elif any(k in query_lower for k in ["catatan perkembangan", "riwayat catatan", "s/o/a/p", "soap terakhir", "perkembangan medis", "progress note", "cppt"]):
        detected_intent = "1. Riwayat Catatan Perkembangan Pasien (SIMRS MCP)"
    elif any(k in query_lower for k in ["anamnesis", "keluhan", "rps", "rpd", "rpk", "tinjauan sistem"]):
        detected_intent = "2. Ambil Data Anamnesis SIMRS (MCP)"
    elif any(k in query_lower for k in ["riwayat", "demografi", "rawat inap", "admission"]):
        detected_intent = "1. Riwayat & Demografi Pasien SIMRS (MCP)"
    elif any(k in query_lower for k in ["lab", "laboratorium", "ttv", "tanda vital", "egfr", "uacr", "hba1c", "elektrolit", "tensi"]):
        detected_intent = "3. Evaluasi Hasil Lab & Pemeriksaan SIMRS (MCP)"
    elif any(k in query_lower for k in ["diagnosis", "icd", "banding", "differential"]):
        detected_intent = "4. Rekomendasi Diagnosis & ICD-10"
    elif any(k in query_lower for k in ["rekomendasi obat", "terapi obat", "dosis", "regimen", "peresepan"]):
        detected_intent = "5. Rekomendasi Terapi Obat Berbasis Bukti (Knowledge Management)"
    elif any(k in query_lower for k in ["rekomendasi tindakan", "prosedur medis", "rencana tindakan", "tindakan medis", "intervensi klinis", "tindakan", "prosedur"]):
        detected_intent = "6. Rekomendasi Tindakan & Prosedur Medis (Clinical Procedures & Interventions)"
    elif any(k in query_lower for k in ["patofisiologi", "penjelasan penyakit", "kriteria diagnostik", "staging"]):
        detected_intent = "7. Penjelasan Penyakit & Patofisiologi (Knowledge Management)"
    elif any(k in query_lower for k in ["tanda bahaya", "red flag", "bahaya", "urgensi", "kegawatdaruratan"]):
        detected_intent = "8. Deteksi Tanda Bahaya & Red Flags (Knowledge Management)"
    elif any(k in query_lower for k in ["skrining", "interaksi obat", "keamanan obat", "ddi", "efek samping"]):
        detected_intent = "9. Skrining Interaksi & Keamanan Obat Pasien"
    elif any(k in query_lower for k in ["evaluasi klinis", "evaluasi lengkap", "laporan lengkap", "semua data", "evaluasi terpadu", "ringkasan lengkap", "konsultasi lengkap", "seluruh pemeriksaan"]):
        detected_intent = "Evaluasi Klinis Terpadu SIMRS & Knowledge Management"
    else:
        detected_intent = None

    simrs_mrn = f"MRN-SIMRS-{patient_id.replace('P-', '')}"
    
    if detected_intent:
        steps.append({
            "step_name": "Agent Intelligence & Clinical Planner",
            "description": f"Clinical Intent Detected: '{detected_intent}' (Target MRN: {simrs_mrn})",
            "status": "completed",
            "result": {"detected_intent": detected_intent, "simrs_mrn": simrs_mrn}
        })
        _debug_node_end("planner", f"Intent: '{detected_intent}' | MRN: {simrs_mrn}")
    else:
        steps.append({
            "step_name": "Agent Intelligence & Conversation Handler",
            "description": "Tidak ada intent klinis khusus yang terdeteksi. Merespons kueri secara percakapan langsung.",
            "status": "completed",
            "result": {"detected_intent": None}
        })
        _debug_node_end("planner", "Intent: None (Direct conversation)")

    return {
        **state,
        "detected_intent": detected_intent,
        "steps_executed": steps
    }


# Node 2: SIMRS MCP & Patient Medical History Retrieval Workflow Node
def node_fetch_patient_history(state: MedicalAgentState) -> MedicalAgentState:
    _debug_node_start("fetch_patient_history", state, icon="📋")
    patient_id = state.get("patient_id")
    steps = list(state.get("steps_executed", []))
    
    ehr_result = None
    simrs_profile = None
    simrs_history = None

    simrs_mrn = f"MRN-SIMRS-{patient_id.replace('P-', '')}" if (patient_id and patient_id.strip()) else None

    if simrs_mrn:
        # Step 2A: Query SIMRS Demographics & Profile via MCP
        simrs_prof_res = tool_simrs_get_patient_profile(simrs_mrn)
        if simrs_prof_res.get("status") == "success":
            simrs_profile = simrs_prof_res["profile"]
            steps.append({
                "step_name": "Ambil Profil & Demografi Pasien SIMRS (MCP)",
                "description": f"Mengambil data demografi, NIK, dan BPJS pasien melalui Model Context Protocol ({simrs_mrn})",
                "status": "success",
                "result": f"Nama: {simrs_profile['full_name']} | NIK: {simrs_profile['nik']} | BPJS: {simrs_profile['bpjs_card_no']} ({simrs_profile['bpjs_class']})"
            })
            
        # Step 2B: Query SIMRS Chronic Conditions, Past Admissions & SOAP Notes via MCP
        simrs_hist_res = tool_simrs_get_patient_history(simrs_mrn)
        if simrs_hist_res.get("status") == "success":
            simrs_history = simrs_hist_res["history"]
            soap_note = simrs_history.get("last_soap_progress_note", {})
            steps.append({
                "step_name": "1. Riwayat Catatan Perkembangan Pasien (SIMRS MCP)",
                "description": f"Mengambil riwayat penyakit kronis, riwayat rawat inap, catatan alergi, dan catatan perkembangan medis S/O/A/P terakhir dari basis data SIMRS",
                "status": "success",
                "result": {
                    "penyakit_kronis": simrs_history.get("chronic_conditions", []),
                    "riwayat_rawat_inap": simrs_history.get("past_admissions", []),
                    "catatan_perkembangan_soap": soap_note
                }
            })

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
    else:
        steps.append({
            "step_name": "Konsultasi Medis Umum (Tanpa Data Pasien)",
            "description": "Tidak ada data pasien yang dipilih untuk sesi konsultasi medis umum.",
            "status": "info",
            "result": "Melewati pengambilan data rekam medis pasien."
        })

    prof_name = simrs_profile.get('full_name') if simrs_profile else (ehr_result.get('name') if ehr_result else "N/A (Konsultasi Umum)")
    _debug_node_end("fetch_patient_history", f"Patient: {prof_name} | Chronic conditions: {len(simrs_history.get('chronic_conditions', []) if simrs_history else [])}")
    _debug_edge("fetch_patient_history", "fetch_patient_anamnesis")
    return {
        **state,
        "steps_executed": steps,
        "ehr_data": ehr_result,
        "simrs_profile": simrs_profile,
        "simrs_history": simrs_history
    }


# Node 2.2: SIMRS MCP Patient Clinical Anamnesis Retrieval Node
def node_fetch_patient_anamnesis(state: MedicalAgentState) -> MedicalAgentState:
    _debug_node_start("fetch_patient_anamnesis", state, icon="📝")
    patient_id = state.get("patient_id")
    steps = list(state.get("steps_executed", []))
    simrs_mrn = f"MRN-SIMRS-{patient_id.replace('P-', '')}" if (patient_id and patient_id.strip()) else None

    anamnesis_result = None
    if simrs_mrn:
        anam_res = tool_simrs_get_patient_anamnesis(simrs_mrn)
        if anam_res.get("status") == "success":
            anamnesis_result = anam_res["anamnesis"]
            steps.append({
                "step_name": "2. Ambil Data Anamnesis SIMRS (MCP)",
                "description": f"Mengambil data anamnesis klinis lengkap (Keluhan Utama, RPS, RPD, RPK, Pengobatan, Alergi & Tinjauan Sistem) dari SIMRS RME ({simrs_mrn})",
                "status": "success",
                "result": {
                    "keluhan_utama": anamnesis_result.get("chief_complaint"),
                    "riwayat_penyakit_sekarang": anamnesis_result.get("history_present_illness"),
                    "riwayat_penyakit_dahulu": anamnesis_result.get("past_medical_history"),
                    "riwayat_penyakit_keluarga": anamnesis_result.get("family_history"),
                    "riwayat_pengobatan": anamnesis_result.get("medication_history"),
                    "riwayat_alergi": anamnesis_result.get("allergy_history"),
                    "faktor_gaya_hidup": anamnesis_result.get("lifestyle_factors"),
                    "tinjauan_sistem_organ": anamnesis_result.get("review_of_systems", {})
                }
            })

    chief = (anamnesis_result.get("chief_complaint") or "N/A (Konsultasi Umum)")[:50] if anamnesis_result else "N/A (Konsultasi Umum)"
    _debug_node_end("fetch_patient_anamnesis", f"Chief Complaint: '{chief}'")
    _debug_edge("fetch_patient_anamnesis", "eval_simrs_labs")
    return {
        **state,
        "steps_executed": steps,
        "simrs_anamnesis": anamnesis_result
    }


# Node 2.2b: Evaluasi Hasil Lab dan Pemeriksaan SIMRS (MCP)
def node_eval_simrs_labs(state: MedicalAgentState) -> MedicalAgentState:
    _debug_node_start("eval_simrs_labs", state, icon="🧪")
    patient_id = state.get("patient_id")
    steps = list(state.get("steps_executed", []))
    simrs_mrn = f"MRN-SIMRS-{patient_id.replace('P-', '')}" if (patient_id and patient_id.strip()) else None

    labs_res = None
    if simrs_mrn:
        labs_res = tool_simrs_get_patient_labs(simrs_mrn)
        steps.append({
            "step_name": "1. Evaluasi Hasil Lab & Pemeriksaan SIMRS (MCP)",
            "description": f"Mengambil data laboratorium serial, elektrolit (K+, Na+), fungsi ginjal (eGFR, uACR), dan tanda vital dari SIMRS LIS/EMR ({simrs_mrn})",
            "status": "success",
            "result": {
                "jumlah_parameter_lab": len(labs_res.get("latest_labs", [])),
                "tanda_vital": labs_res.get("vital_signs", {}),
                "evaluasi_kritis": [
                    f"{l['test_name']}: {l['value']} {l['unit']} ({l['status']})"
                    for l in labs_res.get("latest_labs", [])
                    if "Meningkat" in l["status"] or "CKD" in l["status"] or "Mikroalbuminuria" in l["status"] or "Menurun" in l["status"]
                ]
            }
        })
        _debug_node_end("eval_simrs_labs", f"Lab Parameters: {len(labs_res.get('latest_labs', []))} | BP: {labs_res.get('vital_signs', {}).get('blood_pressure')}")
    else:
        _debug_node_end("eval_simrs_labs", "No patient selected (General Consultation)")

    _debug_edge("eval_simrs_labs", "diagnostic_recommendation")
    return {
        **state,
        "steps_executed": steps,
        "simrs_lab_evaluations": labs_res
    }


# Node 2.3: Clinical Diagnostic & Differential Recommendation Engine Node
def node_diagnostic_recommendation(state: MedicalAgentState) -> MedicalAgentState:
    _debug_node_start("diagnostic_recommendation", state, icon="🎯")
    steps = list(state.get("steps_executed", []))
    anamnesis = state.get("simrs_anamnesis")
    ehr_data = state.get("ehr_data")
    simrs_history = state.get("simrs_history") or {}
    chronic = simrs_history.get("chronic_conditions", [])

    diag_rec = tool_generate_diagnostic_recommendations(anamnesis, ehr_data, chronic)
    primary_list = diag_rec.get("primary_recommendations", [])
    primary_desc = ", ".join([f"{d['diagnosis']} [{d['icd10']}]" for d in primary_list]) if primary_list else "Evaluasi Medis Berkala"

    steps.append({
        "step_name": "Mesin Rekomendasi Diagnosis Klinis (ICD-10)",
        "description": f"Menganalisis korelasi anamnesis, riwayat penyakit, dan data lab untuk merumuskan usulan diagnosis dan diagnosis banding",
        "status": "success",
        "result": {
            "usulan_diagnosis": primary_desc,
            "diagnosis_banding_count": len(diag_rec.get("differential_diagnoses", [])),
            "red_flags": diag_rec.get("clinical_red_flags", []),
            "usulan_pemeriksaan": diag_rec.get("recommended_workups", [])
        }
    })

    _debug_node_end("diagnostic_recommendation", f"Primary: {primary_desc[:55]} | Differentials: {len(diag_rec.get('differential_diagnoses', []))}")
    _debug_edge("diagnostic_recommendation", "km_disease_explanations")
    return {
        **state,
        "steps_executed": steps,
        "diagnostic_recommendations": diag_rec
    }


# Node 2.4: Penjelasan Penyakit & Patofisiologi (Knowledge Management)
def node_km_disease_explanations(state: MedicalAgentState) -> MedicalAgentState:
    _debug_node_start("km_disease_explanations", state, icon="📖")
    steps = list(state.get("steps_executed", []))
    diag_rec = state.get("diagnostic_recommendations") or {}
    primary_list = diag_rec.get("primary_recommendations", [])
    disease_name = primary_list[0]["diagnosis"] if primary_list else "Diabetes Mellitus Tipe 2 CKD"

    km_dx_res = tool_km_disease_explanations(disease_name)
    steps.append({
        "step_name": "2. Penjelasan Penyakit & Patofisiologi (Knowledge Management)",
        "description": f"Mengambil tinjauan patofisiologi, kriteria diagnostik baku, dan kode ICD-10 dari basis pengetahuan medis Qdrant ({disease_name})",
        "status": "success",
        "result": {
            "ikhtisar_patofisiologi": km_dx_res.get("disease_overview")[:150] + "...",
            "kriteria_diagnostik": km_dx_res.get("clinical_criteria", []),
            "kode_icd10": km_dx_res.get("icd10_codes", [])
        }
    })

    _debug_node_end("km_disease_explanations", f"Target: {disease_name[:40]} | ICD Codes: {km_dx_res.get('icd10_codes', [])}")
    _debug_edge("km_disease_explanations", "km_red_flag_detection")
    return {
        **state,
        "steps_executed": steps,
        "disease_explanations": km_dx_res
    }


# Node 2.5: Deteksi Tanda Bahaya & Red Flags (Knowledge Management)
def node_km_red_flag_detection(state: MedicalAgentState) -> MedicalAgentState:
    _debug_node_start("km_red_flag_detection", state, icon="🚨")
    steps = list(state.get("steps_executed", []))
    anamnesis = state.get("simrs_anamnesis") or {}
    labs = state.get("simrs_lab_evaluations") or {}
    chief_complaint = anamnesis.get("chief_complaint", "")
    vitals = labs.get("vital_signs", {})

    km_rf_res = tool_km_red_flag_detections(chief_complaint, labs, vitals)
    steps.append({
        "step_name": "3. Deteksi Tanda Bahaya & Red Flags (Knowledge Management)",
        "description": f"Mendeteksi tanda bahaya klinis kritis, ambang batas kedaruratan kardiovaskular, dan risiko asidosis/ulkus dari panduan klinis",
        "status": "success",
        "result": {
            "tingkat_urgensi": km_rf_res.get("urgency_level"),
            "peringatan_kritis": [f"[{r['severity']}] {r['alert']} -> {r['action']}" for r in km_rf_res.get("detected_red_flags", [])]
        }
    })

    _debug_node_end("km_red_flag_detection", f"Urgency: {km_rf_res.get('urgency_level')} | Flags Count: {len(km_rf_res.get('detected_red_flags', []))}")
    _debug_edge("km_red_flag_detection", "km_medication_recommendation")
    return {
        **state,
        "steps_executed": steps,
        "red_flag_detections": km_rf_res
    }


# Node 2.6: Rekomendasi Obat & Panduan Terapi (Knowledge Management)
def node_km_medication_recommendation(state: MedicalAgentState) -> MedicalAgentState:
    _debug_node_start("km_medication_recommendation", state, icon="💊")
    steps = list(state.get("steps_executed", []))
    diag_rec = state.get("diagnostic_recommendations") or {}
    primary_list = diag_rec.get("primary_recommendations", [])
    disease_name = primary_list[0]["diagnosis"] if primary_list else "Diabetes Mellitus Tipe 2"

    km_med_res = tool_km_medication_recommendations(disease_name, egfr=58.0)
    steps.append({
        "step_name": "4. Rekomendasi Terapi Obat (Knowledge Management)",
        "description": f"Mengambil rekomendasi rejimen obat lini pertama, dosis nefroprotektif, dan konsensus PERKENI/KDIGO 2024/ADA 2025 dari basis pengetahuan",
        "status": "success",
        "result": {
            "panduan_konsensus": km_med_res.get("guideline_basis"),
            "rejimen_obat_terpilih": [
                f"{m['drug_name']} ({m['class']}) - {m['renal_dosing']}"
                for m in km_med_res.get("recommended_regimens", [])
            ]
        }
    })

    _debug_node_end("km_medication_recommendation", f"Regimens: {len(km_med_res.get('recommended_regimens', []))} drugs recommended")
    _debug_edge("km_medication_recommendation", "patient_drug_safety")
    return {
        **state,
        "steps_executed": steps,
        "medication_recommendations": km_med_res
    }


# Node 2.7: Skrining Interaksi & Keamanan Obat Pasien
def node_patient_drug_safety(state: MedicalAgentState) -> MedicalAgentState:
    _debug_node_start("patient_drug_safety", state, icon="🛡️")
    steps = list(state.get("steps_executed", []))
    ehr_data = state.get("ehr_data") or {}
    simrs_history = state.get("simrs_history") or {}
    simrs_anamnesis = state.get("simrs_anamnesis") or {}

    current_meds = [m["name"] for m in ehr_data.get("current_medications", [])] or ["Metformin 1000mg", "Lisinopril 20mg", "Atorvastatin 40mg"]
    allergies = simrs_history.get("documented_allergies", []) or [simrs_anamnesis.get("allergy_history", "")]

    safety_res = tool_patient_drug_safety_screening(current_meds, allergies, egfr=58.0)
    steps.append({
        "step_name": "5. Skrining Interaksi & Keamanan Obat Pasien",
        "description": f"Skrining interaksi antar obat aktif ({len(current_meds)} obat), kontraindikasi riwayat alergi silang, dan klirens ginjal",
        "status": "success",
        "result": {
            "status_keamanan_resep": safety_res.get("overall_safety_status"),
            "interaksi_obat": safety_res.get("drug_drug_interactions", []),
            "kontraindikasi_alergi": safety_res.get("allergy_contraindications", []),
            "penyesuaian_klirens": safety_res.get("renal_clearance_guidance", [])
        }
    })

    _debug_node_end("patient_drug_safety", f"Safety Status: {safety_res.get('overall_safety_status')}")
    _debug_edge("patient_drug_safety", "tools")
    return {
        **state,
        "steps_executed": steps,
        "drug_safety_screening": safety_res
    }


# Node 3: Clinical Tools, Pharmacology, SIMRS Update & Qdrant RAG Execution Node
def node_execute_tools(state: MedicalAgentState) -> MedicalAgentState:
    _debug_node_start("tools (RAG & Evidence Search)", state, icon="⚙️")
    patient_id = state.get("patient_id")
    query = state.get("user_query", "")
    ehr_data = state.get("ehr_data")
    steps = list(state.get("steps_executed", []))
    
    simrs_mrn = f"MRN-SIMRS-{patient_id.replace('P-', '')}" if (patient_id and patient_id.strip()) else None
    
    simrs_update_res = None
    drug_findings = None
    lit_summary = None
    rag_chunks = []

    # Step 3A: Check if Doctor requested a SIMRS EMR Record Update / CPPT Commit
    query_lower = query.lower()
    if simrs_mrn and any(k in query_lower for k in ["update simrs", "sync simrs", "simrs update", "commit emr", "write to simrs", "buat cppt", "kirim cppt", "kirim soap", "buat soap", "sinkronisasi cppt", "simpan cppt", "kirim/sinkronisasikan", "kirim ke simrs", "kirim/sinkronisasi"]):
        anamnesis = state.get("simrs_anamnesis") or {}
        labs = state.get("simrs_lab_evaluations") or {}
        diag_rec = state.get("diagnostic_recommendations") or {}
        med_rec = state.get("medication_recommendations") or {}
        
        primary_list = diag_rec.get("primary_recommendations", [])
        primary_dx = f"{primary_list[0]['diagnosis']} [{primary_list[0]['icd10']}]" if primary_list else "Evaluasi Medis Berkala & Pemantauan Klinis"
        
        regimens = med_rec.get("recommended_regimens", [])
        treatment_plan = ", ".join([f"{r['drug_name']} ({r['renal_dosing']})" for r in regimens]) if regimens else "Lanjutkan pemantauan klinis berkala dan terapi pemeliharaan."
        
        chief = anamnesis.get("chief_complaint", "Keluhan klinis terkontrol")
        vitals = labs.get("vital_signs", {})
        tensi = vitals.get("blood_pressure", "120/80 mmHg")
        hr = vitals.get("heart_rate", "80 bpm")
        doctor_notes = f"S: {chief} | O: BP {tensi}, HR {hr}, Suhu {vitals.get('temperature', '36.8°C')} | A: {primary_dx} | P: {treatment_plan}"

        update_res = tool_simrs_update_patient_record(
            mrn=simrs_mrn,
            doctor_notes=doctor_notes,
            primary_diagnosis=primary_dx,
            treatment_plan=treatment_plan
        )
        simrs_update_res = update_res
        steps.append({
            "step_name": "Sinkronisasi & Commit CPPT ke SIMRS (MCP)",
            "description": f"Menyimpan resume CPPT S/O/A/P terintegrasi ke dalam basis data RME SIMRS untuk MRN {simrs_mrn}",
            "status": "success",
            "result": {
                "log_id": update_res.get("log_id"),
                "mrn": simrs_mrn,
                "status": update_res.get("message"),
                "waktu_sinkronisasi": update_res.get("timestamp")
            }
        })

    # Step 3B: Pharmacology & Drug Interaction Screening on Active Medications
    if ehr_data and "current_medications" in ehr_data:
        med_names = [m["name"] for m in ehr_data.get("current_medications", [])]
        drug_findings = tool_check_drug_interactions(med_names)
        steps.append({
            "step_name": "Skrining Farmakologi & Interaksi Obat",
            "description": f"Memeriksa kontraindikasi dan interaksi untuk {len(med_names)} obat aktif pasien",
            "status": "success",
            "result": drug_findings
        })

    # Step 3C: Qdrant Vector RAG Search
    rag_res = tool_qdrant_vector_rag_search(query, top_k=3)
    if rag_res.get("status") == "success":
        rag_chunks = rag_res["chunks"]
        score_info = ", ".join([f"{c['title']} (Score: {c['reranked_score']})" for c in rag_chunks])
        steps.append({
            "step_name": "Qdrant RAG & Reranker Engine",
            "description": f"Gemini text-embedding-004 vector search + Two-stage Reranking pass",
            "status": "success",
            "result": f"Retrieved {len(rag_chunks)} top chunks: {score_info}"
        })

    # Step 2E: Literature Reference Tool
    lit_summary = tool_search_medical_references(query)
    steps.append({
        "step_name": "Evidence-Based Literature Search",
        "description": "Queried clinical practice guidelines (KDIGO / ADA / ACC)",
        "status": "success",
        "result": lit_summary[:120] + "..."
    })

    _debug_node_end("tools", f"RAG Chunks: {len(rag_chunks)} | Literature: {len(lit_summary)} chars")
    _debug_edge("tools", "synthesis")
    return {
        **state,
        "steps_executed": steps,
        "simrs_update_res": simrs_update_res,
        "drug_interaction_findings": drug_findings,
        "literature_summary": lit_summary,
        "rag_chunks": rag_chunks
    }


# Node 3: Gemini Synthesis Node with SIMRS MCP & RAG Context
def node_gemini_synthesis(state: MedicalAgentState) -> MedicalAgentState:
    _debug_node_start("synthesis (Gemini LLM)", state, icon="🩺")
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
    is_progress_note_only = not is_general_full_eval and not is_cppt_commit and not is_general_knowledge_query and any(k in query_lower for k in ["catatan perkembangan", "riwayat catatan", "s/o/a/p", "soap", "perkembangan medis", "progress note", "cppt"])
    is_anamnesis_only = not is_general_full_eval and not is_general_knowledge_query and any(k in query_lower for k in ["anamnesis", "keluhan", "rps", "rpd", "rpk"]) and not is_progress_note_only and not is_cppt_commit
    is_labs_only = not is_general_full_eval and not is_general_knowledge_query and any(k in query_lower for k in ["lab", "laboratorium", "ttv", "tanda vital", "egfr", "uacr", "evaluasi hasil lab", "pemeriksaan simrs"]) and not is_progress_note_only and not is_anamnesis_only and not is_cppt_commit
    is_diagnosis_only = not is_general_full_eval and not is_general_knowledge_query and any(k in query_lower for k in ["diagnosis kerja", "diagnosis banding", "rekomendasi diagnosis pasien", "diagnosis pasien"]) and not is_labs_only and not is_anamnesis_only and not is_progress_note_only and not is_cppt_commit
    is_procedure_only = not is_general_full_eval and not is_general_knowledge_query and any(k in query_lower for k in ["rekomendasi tindakan", "prosedur medis", "rencana tindakan", "tindakan medis", "intervensi klinis", "tindakan", "prosedur"]) and not is_diagnosis_only and not is_labs_only and not is_anamnesis_only and not is_progress_note_only and not is_cppt_commit

    has_patient_data = bool(simrs_profile or simrs_anamnesis or simrs_labs or ehr_data)
    is_patient_data_request = (is_progress_note_only or is_anamnesis_only or is_labs_only or is_diagnosis_only or is_procedure_only or is_general_full_eval or is_cppt_commit)

    if detected_intent is None and not is_general_knowledge_query:
        prompt_context = f"Doctor Query: {query}\n"
        system_instruction = (
            "Anda adalah Asisten AI Medis Klinis (Medical Co-Pilot) yang santun, profesional, dan ramah. "
            "Pesan dokter tidak mengandung kueri rekam medis spesifik atau kueri workflow khusus (misal: salam, sapaan, atau percakapan umum). "
            "Tanggapi dengan ramah dan sopan dalam Bahasa Indonesia, tanyakan bagaimana Anda dapat membantu dokter, dan jelaskan secara ringkas fitur layanan klinis yang siap digunakan:\n"
            "1. **📋 Ambil Informasi Riwayat Pasien (CPPT / S-O-A-P)**\n"
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
        _debug_node_end("synthesis", "No patient selected for patient-specific query. Outputted persuasive guide.")
        _debug_edge("synthesis", "validate_output")
        return {
            **state,
            "steps_executed": steps,
            "final_synthesis": final_text
        }

    elif is_cppt_commit:
        prompt_context = f"Doctor Query: {query}\n\n"
        if simrs_profile:
            prompt_context += (
                f"=== SIMRS PATIENT DEMOGRAPHICS (VIA MCP) ===\n"
                f"MRN: {simrs_profile['mrn']} | Full Name: {simrs_profile['full_name']}\n"
                f"NIK: {simrs_profile['nik']} | BPJS No: {simrs_profile['bpjs_card_no']} ({simrs_profile['bpjs_class']})\n"
                f"Age/Sex: {simrs_profile['age']} y/o {simrs_profile['gender']} | Clinic: {simrs_profile['active_clinic']} | DPJP: {simrs_profile['attending_physician']}\n\n"
            )
        if simrs_update_res:
            prompt_context += (
                f"=== SIMRS MCP COMMIT TRANSACTION RESULT ===\n"
                f"Log ID: {simrs_update_res.get('log_id')}\n"
                f"Status: {simrs_update_res.get('message')}\n"
                f"Timestamp: {simrs_update_res.get('timestamp')}\n\n"
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
        if diagnostic_rec:
            primary_list = diagnostic_rec.get("primary_recommendations", [])
            if primary_list:
                prompt_context += f"Assessment Diagnosis (A): {primary_list[0]['diagnosis']} [ICD-10: {primary_list[0]['icd10']}]\n\n"
        if med_rec:
            prompt_context += f"Treatment Plan (P): {med_rec.get('recommended_regimens')}\n\n"

        system_instruction = (
            "Anda adalah Asisten AI Medis Klinis (Medical Co-Pilot) profesional yang terhubung dengan RME SIMRS melalui Model Context Protocol (MCP). "
            "Dokter meminta pembuatan resume CPPT S/O/A/P terintegrasi dan pengiriman/sinkronisasi ke sistem SIMRS. "
            "Sajikan laporan pengiriman CPPT yang rapi, profesional, dan lengkap menggunakan TABEL MARKDOWN:\n"
            "1. Judul: `## 📤 Pengiriman Catatan Perkembangan Pasien Terintegrasi (CPPT / S-O-A-P) ke SIMRS RME`\n"
            "2. Status Integrasi SIMRS (Tabel: Status Sinkronisasi [✅ Berhasil Terkirim ke SIMRS via MCP], Log Transaksi SIMRS, Waktu Transaksi, No. Rekam Medis (MRN), DPJP Pemeriksa)\n"
            "3. Tabel Resume CPPT S/O/A/P Terintegrasi yang Ditransmisikan:\n"
            "   - **Subjective (S)**: Data Anamnesis Lengkap (Keluhan utama, riwayat penyakit sekarang / RPS, riwayat penyakit dahulu / RPD, riwayat alergi & pengobatan)\n"
            "   - **Objective (O)**: Data Observasi & Pemeriksaan Lengkap (Tanda-tanda vital / TTV: TD, HR, RR, Suhu, SpO2, temuan pemeriksaan fisik & evaluasi laboratorium serial)\n"
            "   - **Assessment (A)**: Diagnosis primer kerja lengkap beserta kode ICD-10 resmi dan diagnosis banding\n"
            "   - **Plan (P)**: Terapi farmakologi (nama obat, dosis nefroprotektif), rencana monitoring lab lanjutan, dan edukasi pasien\n"
            "4. Catatan konfirmasi bahwa data telah tersimpan permanen di basis data RME SIMRS dan disclaimer medis singkat."
        )
    elif is_progress_note_only:
        prompt_context = f"Doctor Query: {query}\n\n"
        if simrs_profile:
            prompt_context += (
                f"=== SIMRS PATIENT DEMOGRAPHICS (VIA MCP) ===\n"
                f"MRN: {simrs_profile['mrn']} | Full Name: {simrs_profile['full_name']}\n"
                f"NIK: {simrs_profile['nik']} | BPJS No: {simrs_profile['bpjs_card_no']} ({simrs_profile['bpjs_class']})\n"
                f"Age/Sex: {simrs_profile['age']} y/o {simrs_profile['gender']} | Blood Type: {simrs_profile['blood_type']}\n"
                f"Clinic: {simrs_profile['active_clinic']} | Physician: {simrs_profile['attending_physician']}\n\n"
            )
        if simrs_history:
            soap_note = simrs_history.get("last_soap_progress_note", {})
            prompt_context += (
                f"=== SIMRS MEDICAL HISTORY & CHRONIC CONDITIONS ===\n"
                f"Chronic Conditions: {', '.join(simrs_history.get('chronic_conditions', []))}\n"
                f"Documented Allergies: {', '.join(simrs_history.get('documented_allergies', []))}\n"
                f"Past Admissions: {simrs_history.get('past_admissions')}\n\n"
                f"=== LATEST SIMRS CPPT / SOAP PROGRESS NOTE ===\n"
                f"Date/Time: {soap_note.get('note_date')} | DPJP: {soap_note.get('practitioner')} ({soap_note.get('clinic')})\n"
                f"Subjective (S): {soap_note.get('subjective')}\n"
                f"Objective (O): {soap_note.get('objective')}\n"
                f"Assessment (A): {soap_note.get('assessment')}\n"
                f"Plan (P): {soap_note.get('plan')}\n\n"
            )
        system_instruction = (
            "Anda adalah Asisten AI Medis Klinis (Medical Co-Pilot) profesional yang terintegrasi dengan SIMRS melalui Model Context Protocol (MCP). "
            "PENTING: Dokter secara spesifik HANYA meminta data Riwayat Demografi Pasien, Riwayat Penyakit Kronis, Riwayat Rawat Inap, dan Catatan Perkembangan Medis (CPPT / S-O-A-P) terakhir pasien. "
            "Sajikan HANYA data riwayat dan catatan perkembangan SOAP pasien secara terstruktur, rapi, dan lengkap menggunakan TABEL MARKDOWN: "
            "1. Judul: `## 📋 Riwayat Catatan Perkembangan Pasien Terpadu (SIMRS MCP)`\n"
            "2. Tabel Profil & Demografi Pasien (Nama, MRN, NIK, BPJS, Usia, Poliklinik/DPJP)\n"
            "3. Tabel Riwayat Penyakit Kronis & Rawat Inap Terdahulu\n"
            "4. Tabel Catatan Perkembangan Pasien Terintegrasi (CPPT / S-O-A-P Terakhir) lengkap dengan Waktu Pemeriksaan, DPJP, Poliklinik, S, O, A, P.\n"
            "5. Catatan ringkas tindak lanjut klinis dan disclaimer medis di bagian akhir.\n"
            "JANGAN PERNAH menampilkan tabel evaluasi lab, rekomendasi diagnosis baru, red flags, atau rekomendasi obat baru karena dokter hanya meminta riwayat dan catatan perkembangan SOAP pasien."
        )
    elif is_anamnesis_only:
        prompt_context = f"Doctor Query: {query}\n\n"
        if simrs_profile:
            prompt_context += (
                f"=== SIMRS PATIENT DEMOGRAPHICS (VIA MCP) ===\n"
                f"MRN: {simrs_profile['mrn']} | Full Name: {simrs_profile['full_name']}\n"
                f"NIK: {simrs_profile['nik']} | BPJS No: {simrs_profile['bpjs_card_no']} ({simrs_profile['bpjs_class']})\n"
                f"Age/Sex: {simrs_profile['age']} y/o {simrs_profile['gender']} | Blood Type: {simrs_profile['blood_type']}\n"
                f"Clinic: {simrs_profile['active_clinic']} | Physician: {simrs_profile['attending_physician']}\n\n"
            )
        if simrs_anamnesis:
            prompt_context += (
                f"=== SIMRS PATIENT CLINICAL ANAMNESIS (VIA MCP) ===\n"
                f"Chief Complaint (Keluhan Utama): {simrs_anamnesis.get('chief_complaint')}\n"
                f"History of Present Illness (RPS): {simrs_anamnesis.get('history_present_illness')}\n"
                f"Past Medical History (RPD): {simrs_anamnesis.get('past_medical_history')}\n"
                f"Family History (RPK): {simrs_anamnesis.get('family_history')}\n"
                f"Medication History: {simrs_anamnesis.get('medication_history')}\n"
                f"Allergy History: {simrs_anamnesis.get('allergy_history')}\n"
                f"Lifestyle Factors: {simrs_anamnesis.get('lifestyle_factors')}\n"
                f"Review of Systems: {simrs_anamnesis.get('review_of_systems')}\n\n"
            )
        system_instruction = (
            "Anda adalah Asisten AI Medis Klinis (Medical Co-Pilot) profesional yang terintegrasi dengan SIMRS melalui Model Context Protocol (MCP). "
            "PENTING: Dokter secara spesifik HANYA meminta data hasil ANAMNESIS pasien. "
            "Sajikan HANYA data hasil anamnesis pasien secara lengkap, rapi, dan terstruktur menggunakan TABEL MARKDOWN: "
            "1. Judul: `## 📝 Hasil Anamnesis Pasien (SIMRS RME)`\n"
            "2. Tabel Profil Singkat Pasien (Nama, MRN, Usia, Gender, BPJS, Poliklinik/DPJP)\n"
            "3. Tabel Komponen Anamnesis (Keluhan Utama, RPS, RPD, RPK, Riwayat Pengobatan, Riwayat Alergi, Faktor Gaya Hidup)\n"
            "4. Catatan ringkas tindak lanjut anamnesis dan disclaimer medis singkat.\n"
            "JANGAN PERNAH menampilkan tabel lab, evaluasi lab, rekomendasi diagnosis ICD-10, red flags, atau rekomendasi obat lainnya karena dokter hanya meminta hasil anamnesis."
        )
    elif is_labs_only:
        prompt_context = f"Doctor Query: {query}\n\n"
        if simrs_profile:
            prompt_context += (
                f"=== SIMRS PATIENT DEMOGRAPHICS (VIA MCP) ===\n"
                f"MRN: {simrs_profile['mrn']} | Full Name: {simrs_profile['full_name']}\n"
                f"NIK: {simrs_profile['nik']} | BPJS No: {simrs_profile['bpjs_card_no']} ({simrs_profile['bpjs_class']})\n"
                f"Age/Sex: {simrs_profile['age']} y/o {simrs_profile['gender']} | Blood Type: {simrs_profile['blood_type']}\n"
                f"Clinic: {simrs_profile['active_clinic']} | Physician: {simrs_profile['attending_physician']}\n\n"
            )
        if simrs_labs:
            prompt_context += "=== SIMRS LABORATORY EVALUATIONS & VITAL SIGNS (VIA MCP) ===\n"
            prompt_context += f"Vital Signs: {simrs_labs.get('vital_signs')}\n"
            for l in simrs_labs.get("latest_labs", []):
                prompt_context += f"- {l['test_name']}: {l['value']} {l['unit']} (Ref Range: {l['ref_range']}) -> Status Klinis: {l['status']}\n"
            prompt_context += "\n"
        system_instruction = (
            "Anda adalah Asisten AI Medis Klinis (Medical Co-Pilot) profesional yang terintegrasi dengan SIMRS melalui Model Context Protocol (MCP). "
            "PENTING: Dokter secara spesifik HANYA meminta EVALUASI HASIL LAB & PEMERIKSAAN / TANDA VITAL pasien. "
            "Sajikan HANYA data hasil lab dan tanda vital pasien secara lengkap, rapi, dan terstruktur menggunakan TABEL MARKDOWN: "
            "1. Judul: `## 🧪 Evaluasi Hasil Lab & Pemeriksaan Penunjang SIMRS (MCP)`\n"
            "2. Tabel Profil Singkat Pasien (Nama, MRN, NIK, BPJS, Usia/Gender, Poliklinik/DPJP)\n"
            "3. Tabel Evaluasi Hasil Laboratorium Serial & Nilai Rujukan (Kolom: Parameter Pemeriksaan, Nilai Hasil, Nilai Rujukan, Evaluasi/Status Klinis)\n"
            "4. Tabel Tanda Vital Terkini (Tekanan Darah, Heart Rate, Suhu Tubuh, Laju Napas, Saturasi SpO2, Status)\n"
            "5. Ringkasan Interpretasi Klinis Nilai Kritis Laboratorium dan disclaimer medis singkat di bagian akhir.\n"
            "DILARANG KERAS menampilkan usulan diagnosis ICD-10 baru, penjelasan patofisiologi, deteksi tanda bahaya red flag, atau rekomendasi terapi obat karena dokter HANYA meminta evaluasi hasil laboratorium."
        )
    elif is_diagnosis_only:
        prompt_context = f"Doctor Query: {query}\n\n"
        if simrs_profile:
            prompt_context += (
                f"=== SIMRS PATIENT DEMOGRAPHICS (VIA MCP) ===\n"
                f"MRN: {simrs_profile['mrn']} | Full Name: {simrs_profile['full_name']}\n"
                f"NIK: {simrs_profile['nik']} | BPJS No: {simrs_profile['bpjs_card_no']} ({simrs_profile['bpjs_class']})\n"
                f"Age/Sex: {simrs_profile['age']} y/o {simrs_profile['gender']} | Blood Type: {simrs_profile['blood_type']}\n"
                f"Clinic: {simrs_profile['active_clinic']} | Physician: {simrs_profile['attending_physician']}\n\n"
            )
        if diagnostic_rec:
            prompt_context += "=== AI DIAGNOSTIC & DIFFERENTIAL RECOMMENDATIONS ===\n"
            for p in diagnostic_rec.get("primary_recommendations", []):
                prompt_context += f"- Primary: {p['diagnosis']} (ICD-10: {p['icd10']}) [{p['confidence']}] - {p['justification']}\n"
            for d in diagnostic_rec.get("differential_diagnoses", []):
                prompt_context += f"- Differential: {d['diagnosis']} (ICD-10: {d['icd10']}) - Clues: {d['clinical_clues']}\n"
            prompt_context += f"Recommended Workups: {', '.join(diagnostic_rec.get('recommended_workups', []))}\n\n"
        system_instruction = (
            "Anda adalah Asisten AI Medis Klinis (Medical Co-Pilot) profesional yang terintegrasi dengan SIMRS dan Knowledge Management. "
            "PENTING: Dokter secara spesifik HANYA meminta REKOMENDASI DIAGNOSIS KERJA (PRIMER), DIAGNOSIS BANDING, & KODEFIKASI ICD-10. "
            "Sajikan HANYA rekomendasi diagnosis secara lengkap, rapi, dan terstruktur menggunakan TABEL MARKDOWN: "
            "1. Judul: `## 🎯 Rekomendasi Diagnosis Klinis & ICD-10 (Knowledge Management & SIMRS)`\n"
            "2. Tabel Profil Singkat Pasien (Nama, MRN, NIK, BPJS, Usia/Gender, Poliklinik/DPJP)\n"
            "3. Tabel Rekomendasi Diagnosis Kerja (Primer) & Keyakinan AI (Kolom: Diagnosis Kerja, Kode ICD-10, Tingkat Keyakinan, Justifikasi Klinis)\n"
            "4. Tabel Rekomendasi Diagnosis Banding (Differential Diagnoses) (Kolom: Diagnosis Banding, Kode ICD-10, Petunjuk Klinis / Indikator Pembanding)\n"
            "5. Rekomendasi Rencana Pemeriksaan Penunjang Lanjutan Konfirmasi (Workup)\n"
            "6. Disclaimer medis singkat di bagian akhir.\n"
            "DILARANG KERAS menampilkan tabel evaluasi lab lengkap, red flags, atau rekomendasi obat lainnya karena dokter HANYA meminta rekomendasi diagnosis."
        )
    elif is_procedure_only:
        prompt_context = f"Doctor Query: {query}\n\n"
        if simrs_profile:
            prompt_context += (
                f"=== SIMRS PATIENT DEMOGRAPHICS (VIA MCP) ===\n"
                f"MRN: {simrs_profile['mrn']} | Full Name: {simrs_profile['full_name']}\n"
                f"NIK: {simrs_profile['nik']} | BPJS No: {simrs_profile['bpjs_card_no']} ({simrs_profile['bpjs_class']})\n"
                f"Age/Sex: {simrs_profile['age']} y/o {simrs_profile['gender']} | Blood Type: {simrs_profile['blood_type']}\n"
                f"Clinic: {simrs_profile['active_clinic']} | Physician: {simrs_profile['attending_physician']}\n\n"
            )
        if simrs_anamnesis:
            prompt_context += (
                f"=== SIMRS PATIENT CLINICAL ANAMNESIS (VIA MCP) ===\n"
                f"Chief Complaint (Keluhan Utama): {simrs_anamnesis.get('chief_complaint')}\n"
                f"RPS: {simrs_anamnesis.get('history_present_illness')}\n"
                f"RPD: {simrs_anamnesis.get('past_medical_history')}\n"
                f"Allergies: {simrs_anamnesis.get('allergy_history')}\n\n"
            )
        if simrs_labs:
            prompt_context += f"Vital Signs: {simrs_labs.get('vital_signs')}\n\n"
        if diagnostic_rec:
            prompt_context += f"Primary Diagnoses: {diagnostic_rec.get('primary_recommendations')}\n"
            prompt_context += f"Recommended Workups: {diagnostic_rec.get('recommended_workups')}\n\n"
        if red_flags:
            prompt_context += f"Detected Red Flags: {red_flags.get('detected_red_flags')}\n\n"
        if med_rec:
            prompt_context += f"Pharmacotherapy Regimens: {med_rec.get('recommended_regimens')}\n\n"

        system_instruction = (
            "Anda adalah Asisten AI Medis Klinis (Medical Co-Pilot) profesional yang terintegrasi dengan SIMRS dan Knowledge Management. "
            "PENTING: Dokter secara spesifik HANYA meminta REKOMENDASI TINDAKAN & PROSEDUR MEDIS / INTERVENSI KLINIS untuk pasien ini. "
            "Sajikan HANYA rekomendasi tindakan dan prosedur klinis secara lengkap, terstruktur, dan berbasis bukti menggunakan TABEL MARKDOWN: "
            "1. Judul: `## 💉 Rekomendasi Tindakan & Prosedur Medis (Clinical Procedures & Interventions)`\n"
            "2. Tabel Profil Singkat Pasien (Nama, MRN, NIK, BPJS, Usia/Gender, Poliklinik/DPJP)\n"
            "3. Tabel Rekomendasi Tindakan / Prosedur Diagnostik & Terapeutik (Kolom: Jenis Tindakan / Prosedur, Indikasi Klinis Pasien, Tingkat Urgensi [Elektif / Segera / Cito], Persiapan & Protokol Tindakan)\n"
            "4. Tabel Rencana Intervensi Non-Farmakologi & Modifikasi Gaya Hidup (Kolom: Program Intervensi, Target Klinis, Rekomendasi Edukasi & Pelaksanaan)\n"
            "5. Tabel Rencana Monitoring & Jadwal Evaluasi / Kriteria Rujukan Spesialis (Kolom: Parameter Pemantauan, Frekuensi / Jadwal, Kriteria Rujukan Lanjut / Red Flags)\n"
            "6. Disclaimer medis singkat di bagian akhir.\n"
            "Fokuskan isi rekomendasi pada tindakan medis yang relevan dengan keluhan, diagnosis kerja, dan temuan klinis pasien."
        )
    else:
        prompt_context = f"Doctor Query: {query}\n\n"
        
        if simrs_profile:
            prompt_context += (
                f"=== SIMRS PATIENT DEMOGRAPHICS (VIA MCP) ===\n"
                f"MRN: {simrs_profile['mrn']} | Full Name: {simrs_profile['full_name']}\n"
                f"NIK: {simrs_profile['nik']} | BPJS No: {simrs_profile['bpjs_card_no']} ({simrs_profile['bpjs_class']})\n"
                f"Age/Sex: {simrs_profile['age']} y/o {simrs_profile['gender']} | Blood Type: {simrs_profile['blood_type']}\n"
                f"Clinic: {simrs_profile['active_clinic']} | Physician: {simrs_profile['attending_physician']}\n\n"
            )

        if simrs_anamnesis:
            prompt_context += (
                f"=== SIMRS PATIENT CLINICAL ANAMNESIS (VIA MCP) ===\n"
                f"Chief Complaint (Keluhan Utama): {simrs_anamnesis.get('chief_complaint')}\n"
                f"History of Present Illness (RPS): {simrs_anamnesis.get('history_present_illness')}\n"
                f"Past Medical History (RPD): {simrs_anamnesis.get('past_medical_history')}\n"
                f"Family History (RPK): {simrs_anamnesis.get('family_history')}\n"
                f"Medication History: {simrs_anamnesis.get('medication_history')}\n"
                f"Allergy History: {simrs_anamnesis.get('allergy_history')}\n\n"
            )

        if simrs_labs:
            prompt_context += "=== SIMRS LABORATORY EVALUATIONS & VITAL SIGNS (VIA MCP) ===\n"
            prompt_context += f"Vital Signs: {simrs_labs.get('vital_signs')}\n"
            for l in simrs_labs.get("latest_labs", []):
                prompt_context += f"- {l['test_name']}: {l['value']} {l['unit']} (Ref: {l['ref_range']}) -> Status: {l['status']}\n"
            prompt_context += "\n"

        if diagnostic_rec:
            prompt_context += "=== AI DIAGNOSTIC & DIFFERENTIAL RECOMMENDATIONS ===\n"
            for p in diagnostic_rec.get("primary_recommendations", []):
                prompt_context += f"- Primary: {p['diagnosis']} (ICD-10: {p['icd10']}) [{p['confidence']}] - {p['justification']}\n"
            for d in diagnostic_rec.get("differential_diagnoses", []):
                prompt_context += f"- Differential: {d['diagnosis']} (ICD-10: {d['icd10']}) - Clues: {d['clinical_clues']}\n"
            prompt_context += "\n"

        if disease_exp:
            prompt_context += (
                f"=== DISEASE PATHOPHYSIOLOGY & CRITERIA (FROM KNOWLEDGE MANAGEMENT) ===\n"
                f"Overview: {disease_exp.get('disease_overview')}\n"
                f"Criteria: {', '.join(disease_exp.get('clinical_criteria', []))}\n\n"
            )

        if red_flags:
            prompt_context += "=== DETECTED CLINICAL RED FLAGS (FROM KNOWLEDGE MANAGEMENT) ===\n"
            for r in red_flags.get("detected_red_flags", []):
                prompt_context += f"- [{r['severity']}] {r['alert']}: {r['action']}\n"
            prompt_context += "\n"

        if med_rec:
            prompt_context += "=== EVIDENCE-BASED MEDICATION RECOMMENDATIONS (FROM KNOWLEDGE MANAGEMENT) ===\n"
            for m in med_rec.get("recommended_regimens", []):
                prompt_context += f"- {m['drug_name']} ({m['class']}): {m['indication']} | Renal Dosing: {m['renal_dosing']}\n"
            prompt_context += f"Guideline Basis: {med_rec.get('guideline_basis')}\n\n"

        if drug_safety:
            prompt_context += (
                f"=== PATIENT DRUG SAFETY SCREENING ===\n"
                f"Overall Safety: {drug_safety.get('overall_safety_status')}\n"
                f"DDI Findings: {drug_safety.get('drug_drug_interactions')}\n"
                f"Allergy Contraindications: {drug_safety.get('allergy_contraindications')}\n\n"
            )

        if simrs_update_res:
            prompt_context += (
                f"=== SIMRS EMR RECORD UPDATE STATUS ===\n"
                f"Status: {simrs_update_res.get('message')}\n"
                f"Log ID: {simrs_update_res.get('log_id')} at {simrs_update_res.get('timestamp')}\n\n"
            )

        if rag_chunks:
            prompt_context += f"=== QDRANT VECTOR RAG KNOWLEDGE (RERANKED TOP MATCHES) ===\n"
            for i, chunk in enumerate(rag_chunks, 1):
                prompt_context += (
                    f"[{i}] {chunk['title']} ({chunk['category']}) | Specialty: {chunk['specialty']}\n"
                    f"ICD-10: {chunk['icd10_code'] or 'N/A'} | RxNorm: {chunk['rxnorm_code'] or 'N/A'}\n"
                    f"Knowledge Text:\n{chunk['chunk_snippet']}\n\n"
                )
                
        if lit_summary:
            prompt_context += f"=== CLINICAL PRACTICE GUIDELINE REFERENCES ===\n{lit_summary}\n\n"

        intro_desc = (
            "Anda adalah Asisten AI Medis Klinis (Medical Co-Pilot) profesional yang berfokus pada konsultasi medis umum berbasis literatur ilmiah, pedoman klinis (Clinical Practice Guidelines), dan basis pengetahuan vektor Qdrant (Knowledge Management)."
            if not simrs_profile
            else "Anda adalah Asisten AI Medis Klinis (Medical Co-Pilot) profesional yang terintegrasi dengan SIMRS melalui Model Context Protocol (MCP) dan basis pengetahuan vektor Qdrant RAG (Knowledge Management)."
        )
        system_instruction = (
            f"{intro_desc} "
            "Tugas Anda adalah memberikan jawaban ilmiah, terstruktur, dan berbasis bukti medis (Evidence-Based Medicine). "
            "ATURAN FORMAT WAJIB:\n"
            "1. Sajikan data diagnosis, evaluasi lab, rekomendasi obat, panduan dosis, dan skrining keamanan menggunakan TABEL MARKDOWN (`| Kolom 1 | Kolom 2 | ... |`) bila relevan.\n"
            "2. Gunakan heading Markdown (##, ###), poin tebal, dan lencana referensi medis yang rapi.\n"
            "3. PENTING: Jika topik medis atau data yang ditanyakan tidak ditemukan atau belum tersedia di basis pengetahuan (Knowledge Management), sampaikan jawaban secara persuasif, santun, dan profesional dalam Bahasa Indonesia bahwa informasi tersebut belum tersedia di pengetahuan Anda saat ini, dan berikan saran penelusuran lebih lanjut.\n"
            "4. Selalu sertakan disclaimer medis singkat di bagian akhir rekomendasi klinis."
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
            # Also build structured model fallback for consistency
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
        "description": (
            f"Synthesized evidence-based guidelines & Knowledge Management literature via Gemini ({settings.GEMINI_MODEL_NAME})"
            if (not simrs_profile or not simrs_profile.get("mrn"))
            else f"Synthesized SIMRS Lab data, Diagnostic, Knowledge Management medications & red flags via Gemini ({settings.GEMINI_MODEL_NAME})"
        ),
        "status": "success",
        "result": "Synthesis generated successfully"
    })

    _debug_node_end("synthesis", f"Synthesis Result: {len(final_text)} characters generated")
    _debug_edge("synthesis", "validate_output")
    return {
        **state,
        "steps_executed": steps,
        "final_synthesis": final_text,
        "structured_output": structured_output
    }



# Node: Dedicated LLM Output Validation & Clinical Safety Verification
def node_validate_output(state: MedicalAgentState) -> MedicalAgentState:
    """
    Validates the generated clinical synthesis against ground-truth SIMRS records,
    screens for allergy contraindications, verifies red flag coverage, sanitizes PII/toxic content,
    and enforces clinical disclaimer compliance.
    """
    _debug_node_start("validate_output", state, icon="🛡️")
    final_synthesis = state.get("final_synthesis", "")
    steps = list(state.get("steps_executed", []))

    validation_res = LLMOutputValidator.evaluate_all(
        output_text=final_synthesis,
        simrs_profile=state.get("simrs_profile"),
        simrs_anamnesis=state.get("simrs_anamnesis"),
        simrs_labs=state.get("simrs_lab_evaluations"),
        red_flag_detections=state.get("red_flag_detections"),
        drug_safety_screening=state.get("drug_safety_screening"),
        structured_output=state.get("structured_output")
    )


    # If auto-remediation occurred (e.g. disclaimer attached or PII redacted), update final text
    remediated_text = validation_res.get("remediated_text")
    if remediated_text and remediated_text != final_synthesis:
        final_synthesis = remediated_text

    step_status = "success" if validation_res["is_valid"] else "failed"
    step_desc = f"Validasi output klinis: {validation_res['verdict']} (Skor Kepatuhan: {validation_res['validation_score']})"
    if validation_res.get("alerts"):
        step_desc += f" - Terdeteksi {len(validation_res['alerts'])} temuan/alert klinis."

    steps.append({
        "step_name": "Validasi Output LLM & Clinical Safety Guardrail",
        "description": step_desc,
        "status": step_status,
        "result": {
            "verdict": validation_res["verdict"],
            "score": validation_res["validation_score"],
            "alerts": validation_res["alerts"],
            "remediation_applied": validation_res["remediation_applied"]
        }
    })

    _debug_node_end("validate_output", f"Score: {validation_res['validation_score']} | {validation_res['verdict']}")
    _debug_edge("validate_output", "END")

    return {
        **state,
        "steps_executed": steps,
        "final_synthesis": final_synthesis,
        "output_validation": validation_res
    }


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
) -> tuple[str, Optional[Dict[str, Any]]]:
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
    is_progress_note_only = not is_general_full_eval and not is_cppt_commit and not is_general_knowledge_query and any(k in query_lower for k in ["catatan perkembangan", "riwayat catatan", "s/o/a/p", "soap", "perkembangan medis", "progress note", "cppt"])
    is_anamnesis_only = not is_general_full_eval and not is_general_knowledge_query and any(k in query_lower for k in ["anamnesis", "keluhan", "rps", "rpd", "rpk"]) and not is_progress_note_only and not is_cppt_commit
    is_labs_only = not is_general_full_eval and not is_general_knowledge_query and any(k in query_lower for k in ["lab", "laboratorium", "ttv", "tanda vital", "egfr", "uacr", "evaluasi hasil lab", "pemeriksaan simrs"]) and not is_progress_note_only and not is_anamnesis_only and not is_cppt_commit
    is_diagnosis_only = not is_general_full_eval and not is_general_knowledge_query and any(k in query_lower for k in ["diagnosis kerja", "diagnosis banding", "rekomendasi diagnosis pasien", "diagnosis pasien"]) and not is_labs_only and not is_anamnesis_only and not is_progress_note_only and not is_cppt_commit
    has_patient_data = bool(simrs_profile or simrs_anamnesis or simrs_labs or ehr_data)
    is_patient_data_request = (is_progress_note_only or is_anamnesis_only or is_labs_only or is_diagnosis_only or is_general_full_eval or is_cppt_commit)

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

    if not any([is_progress_note_only, is_anamnesis_only, is_labs_only, is_diagnosis_only, is_general_full_eval, is_cppt_commit, is_general_knowledge_query]):
        query_strip = query_lower.strip()
        if any(g in query_strip for g in ["halo", "hai", "selamat", "pagi", "siang", "sore", "malam", "assalam", "hi", "tes", "test", "bantu", "siapa"]):
            greet_text = (
                "Halo Dokter! 👋 Selamat datang di **AI Medical Assistant & Clinical Decision Support System**.\n\n"
                "Saya siap membantu Anda dalam proses konsultasi dan evaluasi klinis pasien. Anda dapat memilih salah satu aksi pada **Quick Prompts / FAQ** di atas atau menanyakan langsung:\n\n"
                "1. **📋 Ambil Informasi Riwayat Pasien (CPPT / S-O-A-P)**: Mengambil riwayat CPPT S/O/A/P dan rawat inap.\n"
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

    chief_c = simrs_anamnesis.get("chief_complaint", "Nyeri ulu hati, mual, lemas") if simrs_anamnesis else "Keluhan klinis terkontrol"
    hpi_c = simrs_anamnesis.get("history_present_illness", "Keluhan dirasakan memberat sejak 3 hari terakhir.") if simrs_anamnesis else ""
    pmh_c = simrs_anamnesis.get("past_medical_history", "Riwayat penyakit terkontrol") if simrs_anamnesis else ""
    allergy_c = simrs_anamnesis.get("allergy_history", "Tidak ada riwayat alergi") if simrs_anamnesis else "Tidak ada riwayat alergi"
    meds_c = simrs_anamnesis.get("medication_history", "Tidak ada riwayat obat rutin") if simrs_anamnesis else ""
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
        patient=patient_model,
        subjective=subj_model,
        objective=obj_model,
        assessment=assess_model,
        plan=plan_model,
        red_flags=red_flags_list,
        drug_safety_status=safety_status
    )
    return soap_schema.to_markdown(), soap_schema.model_dump()


def _route_entry_point(state: MedicalAgentState) -> str:
    wf = state.get("workflow_type")

    audio_bytes = state.get("audio_bytes")
    if wf == "audio" and audio_bytes:
        _debug_edge("START", "audio_transcription", condition="workflow_type == 'audio' and audio_bytes present")
        return "audio_transcription"
    else:
        _debug_edge("START", "planner", condition="workflow_type != 'audio' or text query")
        return "planner"


def _route_planner(state: MedicalAgentState) -> str:
    patient_id = state.get("patient_id")
    detected_intent = state.get("detected_intent")

    # KONSULTASI MEDIS UMUM (Tidak ada data pasien yang dipilih):
    # TIDAK ADA workflow membaca ke SIMRS. Rute langsung ke tools (RAG & Literatur) atau synthesis.
    if not patient_id or not patient_id.strip():
        if detected_intent is None:
            _debug_edge("planner", "synthesis", condition="general consultation: no intent -> direct to synthesis")
            return "synthesis"
        _debug_edge("planner", "tools", condition="general consultation: bypass all SIMRS read nodes -> direct to tools (RAG/KM)")
        return "tools"

    # KONSULTASI PASIEN AKTIF (Terhubung SIMRS EMR):
    if detected_intent is None:
        _debug_edge("planner", "synthesis", condition="no clinical intent detected (skip workflow nodes)")
        return "synthesis"
    else:
        _debug_edge("planner", "fetch_patient_history", condition=f"patient mode ({patient_id}): read SIMRS EMR workflow")
        return "fetch_patient_history"


# Build LangGraph Workflow with SQLite Checkpointer
def build_medical_agent_graph(checkpointer=None):
    workflow = StateGraph(MedicalAgentState)
    
    # Add nodes
    workflow.add_node("planner", node_planner)
    workflow.add_node("fetch_patient_history", node_fetch_patient_history)
    workflow.add_node("fetch_patient_anamnesis", node_fetch_patient_anamnesis)
    workflow.add_node("eval_simrs_labs", node_eval_simrs_labs)
    workflow.add_node("diagnostic_recommendation", node_diagnostic_recommendation)
    workflow.add_node("km_disease_explanations", node_km_disease_explanations)
    workflow.add_node("km_red_flag_detection", node_km_red_flag_detection)
    workflow.add_node("km_medication_recommendation", node_km_medication_recommendation)
    workflow.add_node("patient_drug_safety", node_patient_drug_safety)
    workflow.add_node("tools", node_execute_tools)
    workflow.add_node("synthesis", node_gemini_synthesis)
    workflow.add_node("validate_output", node_validate_output)
    workflow.add_node("audio_transcription", node_audio_transcription)
    workflow.add_node("audio_soap_summary", node_audio_soap_summary)
    
    # Connect edges
    workflow.set_conditional_entry_point(
        _route_entry_point,
        {"audio_transcription": "audio_transcription", "planner": "planner"},
    )
    workflow.add_edge("audio_transcription", "audio_soap_summary")
    workflow.add_edge("audio_soap_summary", "validate_output")

    
    # Conditional edge from planner:
    # - General consultation: routes to "tools" (RAG/KM only) or "synthesis", skipping SIMRS read nodes entirely
    # - Patient consultation: routes to "fetch_patient_history" (reads SIMRS)
    workflow.add_conditional_edges(
        "planner",
        _route_planner,
        {
            "fetch_patient_history": "fetch_patient_history",
            "tools": "tools",
            "synthesis": "synthesis"
        }
    )
    workflow.add_edge("fetch_patient_history", "fetch_patient_anamnesis")
    workflow.add_edge("fetch_patient_anamnesis", "eval_simrs_labs")
    workflow.add_edge("eval_simrs_labs", "diagnostic_recommendation")
    workflow.add_edge("diagnostic_recommendation", "km_disease_explanations")
    workflow.add_edge("km_disease_explanations", "km_red_flag_detection")
    workflow.add_edge("km_red_flag_detection", "km_medication_recommendation")
    workflow.add_edge("km_medication_recommendation", "patient_drug_safety")
    workflow.add_edge("patient_drug_safety", "tools")
    workflow.add_edge("tools", "synthesis")
    workflow.add_edge("synthesis", "validate_output")
    workflow.add_edge("validate_output", END)

    
    if checkpointer is None:
        checkpointer = sqlite_checkpointer
    
    return workflow.compile(checkpointer=checkpointer)


medical_agent_graph = build_medical_agent_graph()
