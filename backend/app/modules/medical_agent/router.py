import os
import json
import asyncio
import re
from uuid import uuid4
from datetime import datetime
# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
# pyrefly: ignore [missing-import]
from fastapi.responses import StreamingResponse, FileResponse
from app.core.security import get_current_user, TokenPayload, require_role
from app.core.database import dbApplication
from app.core.config import settings
from app.modules.medical_agent import (
    AgentChatRequest, AgentChatResponse, SOAContentSchema, SOANoteSchema,
    SOAReviewRequest, SOAReviewResponse, SOAConfirmationRequest,
    TempSOAPContentSchema, TempSOAPRecordSchema, TempSOAPUpdateRequest,
    TempSOAPCommitResponse,
    medical_agent_graph
)
from app.modules.medical_agent.tools.simrs_tools import tool_simrs_update_patient_record

AUDIO_STORAGE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../uploads/audio"))
os.makedirs(AUDIO_STORAGE_DIR, exist_ok=True)

router = APIRouter(prefix="/agent", tags=["Medical Agent"])


def _soap_section(markdown: str, heading: str) -> str:
    """Extracts S, O, A, P, or I sections from clinical Markdown synthesis reliably."""
    if not markdown:
        return "Tidak disebutkan."

    first_letter = heading[0].upper()

    # Map heading synonyms
    synonyms = [heading]
    if heading.lower() == "subjective":
        synonyms.extend(["Subjektif", "Anamnesis", "Hasil Anamnesis"])
    elif heading.lower() == "objective":
        synonyms.extend(["Objektif", "Pemeriksaan Fisik", "Pemeriksaan", "Evaluasi Hasil Lab", "Tanda Vital"])
    elif heading.lower() == "assessment":
        synonyms.extend(["Asesmen", "Diagnosis", "Diagnosa", "Diagnosis Utama", "Rekomendasi Diagnosis"])
    elif heading.lower() == "plan":
        synonyms.extend(["Plan", "Penatalaksanaan", "Tata Laksana", "Rencana Terapi", "Rencana", "Rekomendasi Terapi"])
    elif heading.lower() in ("instruksi", "instruction"):
        synonyms.extend(["Instruksi", "Instruksi Klinis", "Edukasi", "Edukasi Pasien", "Tanda Bahaya", "PPA"])

    synonyms_regex = "|".join([re.escape(s) for s in synonyms])

    # Pattern matches starting header e.g. ### 💊 P — Plan, ### P - Plan, ### Plan, **Plan:**, etc.
    header_pattern = rf"(?:^|\n)(?:###|\*\*|##)\s*(?:[👤🔬🎯💊📝🚨💡📌]\s*)?(?:{first_letter}\s*[—\-\(:\.]\s*(?:{synonyms_regex})|{synonyms_regex})[^\n]*\n"

    start_match = re.search(header_pattern, markdown, flags=re.IGNORECASE)
    if not start_match:
        # Try finding loose header
        header_pattern_simple = rf"(?:^|\n)(?:###|##|\*\*)\s*.*?(?:{synonyms_regex}).*?\n"
        start_match = re.search(header_pattern_simple, markdown, flags=re.IGNORECASE)

    if not start_match:
        return "Tidak disebutkan."

    start_pos = start_match.end()
    rest = markdown[start_pos:]

    # Find the next section boundary (next ### / ## header, horizontal rule, disclaimer, or end of text)
    end_pattern = r"(?:^|\n)(?:(?:###|\*\*|##)\s*(?:[👤🔬🎯💊📝🚨💡📌]\s*)?(?:[SOAPI]\s*[—\-\(:\.]|Subjective|Objective|Assessment|Plan|Instruksi|Edukasi|Transkrip|Status Transaksi|Demografi)|---\n|\*\(⚠️)"
    end_match = re.search(end_pattern, rest, flags=re.IGNORECASE)

    extracted = rest[:end_match.start()].strip() if end_match else rest.strip()

    # Strip any trailing disclaimer or hr if present
    extracted = re.sub(r"\n*---\n*\*\(⚠️.*?\)\*?", "", extracted, flags=re.DOTALL).strip()

    return extracted if extracted else "Tidak disebutkan."


_soa_section = _soap_section


def _extract_soap_from_state(final_state: dict) -> dict:
    """
    Extracts Subjective, Objective, Assessment, Plan, and Instructions from
    either the structured Pydantic model (structured_output) or Markdown synthesis.
    """
    struct = final_state.get("structured_output")
    soap_obj = None
    if isinstance(struct, dict):
        soap_obj = struct.get("soap") or (struct if ("subjective" in struct and "assessment" in struct) else None)

    # 1. First priority: Extract from structured Pydantic Output
    if soap_obj and isinstance(soap_obj, dict):
        subj = soap_obj.get("subjective", {})
        s_lines = []
        if isinstance(subj, dict):
            if subj.get("chief_complaint"): s_lines.append(f"- Keluhan Utama: {subj['chief_complaint']}")
            if subj.get("history_present_illness"): s_lines.append(f"- RPS: {subj['history_present_illness']}")
            if subj.get("past_medical_history"): s_lines.append(f"- RPD: {subj['past_medical_history']}")
            if subj.get("allergy_history"): s_lines.append(f"- Riwayat Alergi: {subj['allergy_history']}")
            if subj.get("medication_history"): s_lines.append(f"- Riwayat Obat: {subj['medication_history']}")
        s_text = "\n".join(s_lines) if s_lines else ""

        obj = soap_obj.get("objective", {})
        o_lines = []
        if isinstance(obj, dict):
            vs = obj.get("vital_signs", {})
            if isinstance(vs, dict):
                vs_parts = [f"{k.replace('_', ' ').title()}: {v}" for k, v in vs.items() if v]
                if vs_parts: o_lines.append(f"- Tanda Vital: {', '.join(vs_parts)}")
            if obj.get("physical_examination"):
                o_lines.append(f"- Pemeriksaan Fisik: {obj['physical_examination']}")
            labs = obj.get("laboratory_results", [])
            if isinstance(labs, list) and labs:
                lab_parts = [f"{l.get('test_name')}: {l.get('value')} {l.get('unit', '')} ({l.get('status', 'Normal')})" for l in labs if isinstance(l, dict)]
                if lab_parts: o_lines.append(f"- Laboratorium: {', '.join(lab_parts)}")
        o_text = "\n".join(o_lines) if o_lines else ""

        ass = soap_obj.get("assessment", {})
        a_lines = []
        if isinstance(ass, dict):
            pd = ass.get("primary_diagnosis", {})
            if isinstance(pd, dict) and pd.get("diagnosis"):
                icd = f" [ICD-10: {pd.get('icd10')}]" if pd.get("icd10") else ""
                conf = f" (Keyakinan: {int(float(pd.get('confidence', 0))*100)}%)" if pd.get("confidence") else ""
                a_lines.append(f"- Diagnosis Primer: {pd.get('diagnosis')}{icd}{conf}")
            diffs = ass.get("differential_diagnoses", [])
            if isinstance(diffs, list) and diffs:
                for d in diffs:
                    if isinstance(d, dict) and d.get("diagnosis"):
                        d_icd = f" [ICD-10: {d.get('icd10')}]" if d.get("icd10") else ""
                        a_lines.append(f"- Diagnosis Banding: {d.get('diagnosis')}{d_icd}")
            if ass.get("clinical_reasoning"):
                a_lines.append(f"- Penalaran Klinis: {ass['clinical_reasoning']}")
        a_text = "\n".join(a_lines) if a_lines else ""

        pl = soap_obj.get("plan", {})
        p_lines = []
        i_lines = []
        if isinstance(pl, dict):
            meds = pl.get("medications", [])
            if isinstance(meds, list) and meds:
                p_lines.append("- Rekomendasi Terapi Obat:")
                for m in meds:
                    if isinstance(m, dict) and m.get("drug_name"):
                        notes = f" ({m.get('notes')})" if m.get("notes") else ""
                        p_lines.append(f"  • {m.get('drug_name')} {m.get('dosage', '')} {m.get('frequency', '')} {m.get('route', 'Oral')}{notes}".strip())
            if pl.get("diagnostic_workup"):
                dw = pl["diagnostic_workup"]
                p_lines.append(f"- Pemeriksaan Lanjutan: {', '.join(dw) if isinstance(dw, list) else str(dw)}")
            if pl.get("clinical_procedures"):
                cp = pl["clinical_procedures"]
                p_lines.append(f"- Prosedur / Tindakan: {', '.join(cp) if isinstance(cp, list) else str(cp)}")
            if pl.get("follow_up"):
                p_lines.append(f"- Rencana Kontrol / Tindak Lanjut: {pl['follow_up']}")

            if pl.get("patient_education"):
                pe = pl["patient_education"]
                if isinstance(pe, list):
                    for edu in pe: i_lines.append(f"- Edukasi Pasien: {edu}")
                else:
                    i_lines.append(f"- Edukasi Pasien: {pe}")

        red_flags = soap_obj.get("red_flags", [])
        if isinstance(red_flags, list) and red_flags:
            for rf in red_flags:
                if isinstance(rf, dict) and rf.get("title"):
                    i_lines.append(f"- Tanda Bahaya (Red Flag) [{rf.get('severity', 'Warning')}]: {rf.get('title')} — {rf.get('action_required', 'Monitoring')}")

        p_text = "\n".join(p_lines) if p_lines else ""
        i_text = "\n".join(i_lines) if i_lines else ""

        raw_md = final_state.get("final_synthesis", "")
        return {
            "subjective": s_text or _soap_section(raw_md, "Subjective"),
            "objective": o_text or _soap_section(raw_md, "Objective"),
            "assessment": a_text or _soap_section(raw_md, "Assessment"),
            "plan": p_text or _soap_section(raw_md, "Plan"),
            "instructions": i_text or (_soap_section(raw_md, "Instruksi") if ("Instruksi" in raw_md or "Edukasi" in raw_md) else "Sesuai edukasi dan tata laksana klinis terpadu.")
        }

    # 2. Second priority: Parse directly from Markdown using _soap_section
    raw_md = final_state.get("final_synthesis", "")
    return {
        "subjective": _soap_section(raw_md, "Subjective"),
        "objective": _soap_section(raw_md, "Objective"),
        "assessment": _soap_section(raw_md, "Assessment"),
        "plan": _soap_section(raw_md, "Plan"),
        "instructions": _soap_section(raw_md, "Instruksi") if ("Instruksi" in raw_md or "Edukasi" in raw_md) else "Sesuai edukasi dan tata laksana klinis terpadu."
    }


def _create_soap_note(final_synthesis: str, session_id: str, user_id: str, final_state: dict | None = None) -> dict:
    now = datetime.now().isoformat()
    if final_state:
        extracted = _extract_soap_from_state(final_state)
    else:
        extracted = {
            "subjective": _soap_section(final_synthesis, "Subjective"),
            "objective": _soap_section(final_synthesis, "Objective"),
            "assessment": _soap_section(final_synthesis, "Assessment"),
            "plan": _soap_section(final_synthesis, "Plan"),
        }
    note = {
        "note_id": f"soap-{uuid4().hex}",
        "session_id": session_id,
        "user_id": user_id,
        "content": extracted,
        "status": "draft",
        "pending_content": None,
        "changes": [],
        "updated_at": now,
    }
    dbApplication.soap_notes[note["note_id"]] = note
    return note


_create_soa_note = _create_soap_note


def _serialize_soa_note(note: dict) -> SOANoteSchema:
    return SOANoteSchema(**note)


def _get_owned_soa_note(note_id: str, current_user: TokenPayload) -> dict:
    note = dbApplication.soap_notes.get(note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Resume S/O/A/P tidak ditemukan.")
    if current_user.role != "admin" and note["user_id"] != current_user.sub:
        raise HTTPException(status_code=403, detail="Forbidden access to S/O/A/P resume")
    return note

@router.post("/chat", response_model=AgentChatResponse)
def execute_agent_chat(
    request: AgentChatRequest,
    current_user: TokenPayload = Depends(require_role(["doctor", "admin"]))
):
    session_id = request.session_id or f"session-{int(datetime.now().timestamp())}"
    initial_state = {
        "messages": [{"role": "user", "content": request.user_query}],
        "patient_id": request.patient_id,
        "session_id": session_id,
        "user_query": request.user_query,
        "workflow_type": "text",
        "audio_bytes": None,
        "audio_filename": None,
        "audio_transcript": None,
        "audio_error": None,
        "steps_executed": [],
        "ehr_data": None,
        "drug_interaction_findings": None,
        "literature_summary": None,
        "final_synthesis": "",
    }
    turn_thread_id = f"{session_id}-turn-{int(datetime.now().timestamp() * 1000)}"
    config = {"configurable": {"thread_id": turn_thread_id}}

    # Run LangGraph StateGraph with isolated memory per chat turn
    final_state = medical_agent_graph.invoke(initial_state, config=config)
    
    # Update DB session & history
    doctor_name = current_user.email
    user_rec = dbApplication.users.get(current_user.sub)
    if user_rec:
        doctor_name = user_rec["name"]
        
    if session_id not in dbApplication.chat_sessions:
        dbApplication.chat_sessions[session_id] = {
            "session_id": session_id,
            "user_id": current_user.sub,
            "title": request.user_query[:40] + ("..." if len(request.user_query) > 40 else ""),
            "created_at": datetime.now().isoformat(),
            "patient_id": request.patient_id,
            "messages": []
        }
        
    dbApplication.chat_sessions[session_id]["messages"].append({
        "role": "user",
        "content": request.user_query,
        "timestamp": datetime.now().isoformat()
    })
    dbApplication.chat_sessions[session_id]["messages"].append({
        "role": "assistant",
        "content": final_state["final_synthesis"],
        "timestamp": datetime.now().isoformat(),
        "metadata": {
            "steps": final_state.get("steps_executed", [])
        }
    })
    
    # Log action in audit trail
    dbApplication.audit_logs.insert(0, {
        "id": f"log-{len(dbApplication.audit_logs)+1}",
        "timestamp": datetime.now().isoformat(),
        "user_id": current_user.sub,
        "doctor_name": doctor_name,
        "action": "LangGraph Medical Agent Execution",
        "details": f"Query: '{request.user_query[:50]}' | Patient: {request.patient_id or 'N/A'}",
        "tokens_used": 750 + len(final_state["final_synthesis"]) // 4,
        "status": "Success"
    })
    
    return AgentChatResponse(
        session_id=session_id,
        user_query=request.user_query,
        patient_id=request.patient_id,
        steps_executed=final_state["steps_executed"],
        final_synthesis=final_state["final_synthesis"],
        workflow_type="text",
        output_validation=final_state.get("output_validation"),
        structured_output=final_state.get("structured_output"),
    )




import subprocess

def convert_audio_to_wav_ffmpeg(audio_bytes: bytes, filename: str = "audio") -> bytes:
    """Convert MP3/WAV/other audio streams into standard 16kHz 16-bit mono WAV bytes for AI processing."""
    if filename.lower().endswith(".wav") and len(audio_bytes) > 12 and audio_bytes[:4] == b"RIFF" and audio_bytes[8:12] == b"WAVE":
        return audio_bytes

    try:
        cmd = [
            "ffmpeg", "-y", "-i", "pipe:0",
            "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le",
            "-f", "wav", "pipe:1"
        ]
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = proc.communicate(input=audio_bytes)
        if proc.returncode != 0 or not stdout:
            err_msg = stderr.decode(errors="ignore")[:160]
            raise RuntimeError(f"FFmpeg conversion failed: {err_msg}")
        return stdout
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Gagal mengonversi file audio '{filename}' ke WAV: {str(e)}"
        )


@router.post("/chat/audio", response_model=AgentChatResponse)
async def execute_audio_chat(
    audio: UploadFile = File(...),
    patient_id: str | None = Form(None),
    session_id: str | None = Form(None),
    current_user: TokenPayload = Depends(require_role(["doctor", "admin"])),
):
    """Process a WAV or MP3 recording through Gemini STT with Speaker Diarization, produce structured SOAP summary and persist as temp SOAP before SIMRS sync."""
    filename = audio.filename or "audio.mp3"
    allowed_exts = (".wav", ".mp3", ".mpeg", ".m4a", ".ogg")
    if not any(filename.lower().endswith(ext) for ext in allowed_exts):
        raise HTTPException(status_code=415, detail="Format audio tidak didukung. Harap unggah file audio MP3 atau WAV.")

    raw_audio_bytes = await audio.read()
    if not raw_audio_bytes:
        raise HTTPException(status_code=400, detail="File audio kosong.")
    if len(raw_audio_bytes) > settings.MAX_AUDIO_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"Ukuran audio melebihi batas {settings.MAX_AUDIO_UPLOAD_BYTES // (1024 * 1024)} MB.",
        )

    # Convert MP3 / audio formats to standard 16kHz mono WAV for processing
    audio_bytes = convert_audio_to_wav_ffmpeg(raw_audio_bytes, filename=filename)

    audio_label = f"[Rekaman Audio] {filename}"
    initial_state = {
        "messages": [{"role": "user", "content": audio_label}],
        "patient_id": patient_id,
        "user_query": audio_label,
        "workflow_type": "audio",
        "audio_bytes": audio_bytes,
        "audio_filename": filename,
        "audio_mime_type": "audio/wav",
        "audio_transcript": None,
        "audio_error": None,
        "steps_executed": [],
        "ehr_data": None,
        "drug_interaction_findings": None,
        "literature_summary": None,
        "final_synthesis": "",
    }
    resolved_session_id = session_id or f"session-{int(datetime.now().timestamp())}"
    turn_thread_id = f"{resolved_session_id}-turn-{int(datetime.now().timestamp() * 1000)}"
    config = {"configurable": {"thread_id": turn_thread_id}}
    final_state = medical_agent_graph.invoke(initial_state, config=config)

    # Ensure chat session exists
    if resolved_session_id not in dbApplication.chat_sessions:
        dbApplication.chat_sessions[resolved_session_id] = {
            "session_id": resolved_session_id,
            "user_id": current_user.sub,
            "title": f"Audio: {filename}"[:40],
            "created_at": datetime.now().isoformat(),
            "patient_id": patient_id,
            "temp_soap_id": None,
            "messages": [],
        }
    elif current_user.role != "admin" and dbApplication.chat_sessions[resolved_session_id]["user_id"] != current_user.sub:
        raise HTTPException(status_code=403, detail="Forbidden access to chat session")

    # Persist audio file to disk
    file_unique_id = uuid4().hex[:8]
    saved_filename = f"rec_{file_unique_id}_{filename}"
    saved_filepath = os.path.join(AUDIO_STORAGE_DIR, saved_filename)
    try:
        with open(saved_filepath, "wb") as f:
            f.write(audio_bytes)
    except Exception as e:
        print(f"Error saving audio file: {e}")

    # Resolve doctor & patient metadata
    doctor_name = current_user.email
    user_rec = dbApplication.users.get(current_user.sub)
    if user_rec:
        doctor_name = user_rec.get("name", current_user.email)

    patient_name = None
    mrn = None
    nik = None
    if patient_id and patient_id in dbApplication.patient_records:
        pat_rec = dbApplication.patient_records[patient_id]
        patient_name = pat_rec.get("name")
        mrn = pat_rec.get("patient_id")
        nik = pat_rec.get("nik")
    elif patient_id:
        patient_name = "Eleanor Vance"
        mrn = f"MRN-SIMRS-{patient_id.replace('P-', '')}"

    # Extract clean SOAP content
    soap_content_dict = _extract_soap_from_state(final_state)

    # Create Temp SOAP record in application database
    temp_soap_rec = None
    soa_note = None
    if final_state.get("audio_transcript") and not final_state.get("audio_error"):
        soa_note = _create_soap_note(final_state["final_synthesis"], resolved_session_id, current_user.sub, final_state=final_state)
        temp_soap_rec = dbApplication.create_temp_soap(
            session_id=resolved_session_id,
            patient_id=patient_id,
            user_id=current_user.sub,
            doctor_name=doctor_name,
            audio_filename=filename,
            audio_url=f"/api/v1/agent/soap-temp/audio-file/{saved_filename}",
            audio_path=saved_filepath,
            audio_size_bytes=len(raw_audio_bytes),
            audio_transcript=final_state.get("audio_transcript") or "",
            soap_content=soap_content_dict,
            raw_markdown=final_state["final_synthesis"],
            structured_output=final_state.get("structured_output"),
            patient_name=patient_name,
            mrn=mrn,
            nik=nik,
        )
        dbApplication.chat_sessions[resolved_session_id]["temp_soap_id"] = temp_soap_rec["temp_id"]

    dbApplication.chat_sessions[resolved_session_id]["messages"].extend([
        {"role": "user", "content": audio_label, "timestamp": datetime.now().isoformat()},
        {
            "role": "assistant",
            "content": final_state["final_synthesis"],
            "timestamp": datetime.now().isoformat(),
            "metadata": {
                "type": "temp_soap" if temp_soap_rec else ("soa_note" if soa_note else None),
                "temp_id": temp_soap_rec["temp_id"] if temp_soap_rec else None,
                "temp_soap": temp_soap_rec,
                "audio_url": temp_soap_rec["audio_url"] if temp_soap_rec else None,
                "note": soa_note,
                "steps": final_state.get("steps_executed", []),
            },
        },
    ])
    dbApplication.audit_logs.insert(0, {
        "id": f"log-{len(dbApplication.audit_logs) + 1}",
        "timestamp": datetime.now().isoformat(),
        "user_id": current_user.sub,
        "doctor_name": doctor_name,
        "action": "Gemini Audio STT & Temporary SOAP Created",
        "details": f"Audio: '{filename}' | Patient: {patient_id or 'N/A'} | Temp SOAP: {temp_soap_rec['temp_id'] if temp_soap_rec else 'N/A'}",
        "tokens_used": len(final_state["final_synthesis"]) // 4,
        "status": "Success" if not final_state.get("audio_error") else "Failed",
    })
    return AgentChatResponse(
        session_id=resolved_session_id,
        user_query=audio_label,
        patient_id=patient_id,
        steps_executed=final_state["steps_executed"],
        final_synthesis=final_state["final_synthesis"],
        workflow_type="audio",
        audio_transcript=final_state.get("audio_transcript"),
        soa_note=_serialize_soa_note(soa_note) if soa_note else None,
        temp_soap=TempSOAPRecordSchema(**temp_soap_rec) if temp_soap_rec else None,
        output_validation=final_state.get("output_validation"),
        structured_output=final_state.get("structured_output"),
    )


# ── Temporary SOAP Pre-SIMRS Endpoints ──────────────────────────────

@router.get("/soap-temp", response_model=list[TempSOAPRecordSchema])
def list_temp_soap(
    patient_id: str | None = None,
    status: str | None = None,
    session_id: str | None = None,
    limit: int | None = None,
    current_user: TokenPayload = Depends(require_role(["doctor", "admin"]))
):
    """Retrieve list of temporary SOAP records, filtered by patient, status, or session."""
    user_id = None if current_user.role == "admin" else current_user.sub
    records = dbApplication.list_temp_soap(
        user_id=user_id,
        patient_id=patient_id,
        status=status,
        session_id=session_id,
        limit=limit
    )
    return [TempSOAPRecordSchema(**r) for r in records]


@router.get("/soap-temp/{temp_id}", response_model=TempSOAPRecordSchema)
def get_temp_soap(
    temp_id: str,
    current_user: TokenPayload = Depends(require_role(["doctor", "admin"]))
):
    """Retrieve detailed temporary SOAP record by temp_id."""
    rec = dbApplication.get_temp_soap(temp_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Data SOAP Temp tidak ditemukan.")
    if current_user.role != "admin" and rec["user_id"] != current_user.sub:
        raise HTTPException(status_code=403, detail="Akses ditolak untuk data SOAP Temp ini.")
    return TempSOAPRecordSchema(**rec)


@router.get("/soap-temp/session/{session_id}", response_model=TempSOAPRecordSchema | None)
def get_temp_soap_by_session(
    session_id: str,
    current_user: TokenPayload = Depends(require_role(["doctor", "admin"]))
):
    """Retrieve temporary SOAP record associated with a chat session."""
    rec = dbApplication.get_temp_soap_by_session(session_id)
    if not rec:
        return None
    if current_user.role != "admin" and rec["user_id"] != current_user.sub:
        raise HTTPException(status_code=403, detail="Akses ditolak untuk data SOAP Temp ini.")
    return TempSOAPRecordSchema(**rec)


@router.put("/soap-temp/{temp_id}", response_model=TempSOAPRecordSchema)
def update_temp_soap(
    temp_id: str,
    request: TempSOAPUpdateRequest,
    current_user: TokenPayload = Depends(require_role(["doctor", "admin"]))
):
    """Update temporary SOAP content or status before pushing to SIMRS."""
    rec = dbApplication.get_temp_soap(temp_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Data SOAP Temp tidak ditemukan.")
    if current_user.role != "admin" and rec["user_id"] != current_user.sub:
        raise HTTPException(status_code=403, detail="Akses ditolak untuk data SOAP Temp ini.")

    updates = {}
    if request.soap_content is not None:
        updates["soap_content"] = request.soap_content.model_dump()
    if request.raw_markdown is not None:
        updates["raw_markdown"] = request.raw_markdown
    if request.status is not None:
        updates["status"] = request.status

    updated = dbApplication.update_temp_soap(temp_id, updates)
    dbApplication.audit_logs.insert(0, {
        "id": f"log-{len(dbApplication.audit_logs) + 1}",
        "timestamp": datetime.now().isoformat(),
        "user_id": current_user.sub,
        "doctor_name": current_user.email,
        "action": "SOAP Temp Record Updated",
        "details": f"Temp ID: {temp_id} | Status: {updated.get('status')}",
        "tokens_used": 0,
        "status": "Success",
    })
    return TempSOAPRecordSchema(**updated)


@router.delete("/soap-temp/{temp_id}")
def delete_temp_soap(
    temp_id: str,
    current_user: TokenPayload = Depends(require_role(["doctor", "admin"]))
):
    """Delete a temporary SOAP record."""
    rec = dbApplication.get_temp_soap(temp_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Data SOAP Temp tidak ditemukan.")
    if current_user.role != "admin" and rec["user_id"] != current_user.sub:
        raise HTTPException(status_code=403, detail="Akses ditolak untuk data SOAP Temp ini.")

    # Remove audio file if exists
    if rec.get("audio_path") and os.path.exists(rec["audio_path"]):
        try:
            os.remove(rec["audio_path"])
        except Exception:
            pass

    deleted = dbApplication.delete_temp_soap(temp_id)
    return {"status": "deleted", "temp_id": temp_id, "success": deleted}


@router.post("/soap-temp/{temp_id}/commit-simrs", response_model=TempSOAPCommitResponse)
def commit_temp_soap_to_simrs(
    temp_id: str,
    current_user: TokenPayload = Depends(require_role(["doctor", "admin"]))
):
    """Pushes/commits the validated Temporary SOAP record into SIMRS EMR system via MCP."""
    rec = dbApplication.get_temp_soap(temp_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Data SOAP Temp tidak ditemukan.")
    if current_user.role != "admin" and rec["user_id"] != current_user.sub:
        raise HTTPException(status_code=403, detail="Akses ditolak untuk data SOAP Temp ini.")

    # Resolve MRN
    mrn = rec.get("mrn")
    if not mrn:
        pat_id = rec.get("patient_id") or "P-10492"
        mrn = f"MRN-SIMRS-{pat_id.replace('P-', '')}"

    soap_content = rec.get("soap_content", {})
    subj = soap_content.get("subjective", "")
    obj = soap_content.get("objective", "")
    ass = soap_content.get("assessment", "")
    plan = soap_content.get("plan", "")
    inst = soap_content.get("instructions", "")

    doctor_notes = f"S: {subj}\nO: {obj}"
    primary_diagnosis = ass or "Evaluasi Klinis Terpadu"
    treatment_plan = f"P: {plan}\nI: {inst or '-'}"

    simrs_res = tool_simrs_update_patient_record(
        mrn=mrn,
        doctor_notes=doctor_notes,
        primary_diagnosis=primary_diagnosis,
        treatment_plan=treatment_plan
    )

    updated_rec = dbApplication.mark_temp_soap_synced(temp_id, simrs_res)

    # Append confirmation into chat session if exists
    sess_id = rec.get("session_id")
    if sess_id and sess_id in dbApplication.chat_sessions:
        confirm_msg = (
            f"✅ **Catatan CPPT S-O-A-P berhasil disinkronisasikan ke SIMRS!**\n\n"
            f"- **No. Rekam Medis**: `{mrn}`\n"
            f"- **Pasien**: {rec.get('patient_name') or 'Pasien SIMRS'}\n"
            f"- **Diagnosa Utama**: {primary_diagnosis}\n"
            f"- **Nomor Log Transaksi SIMRS**: `{simrs_res.get('log_id', 'LOG-SIMRS-OK')}`\n"
            f"- **Waktu Sinkronisasi**: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
        )
        dbApplication.chat_sessions[sess_id]["messages"].append({
            "role": "assistant",
            "content": confirm_msg,
            "timestamp": datetime.now().isoformat(),
            "metadata": {
                "type": "simrs_sync_result",
                "temp_id": temp_id,
                "simrs_response": simrs_res
            }
        })

    # Audit log
    dbApplication.audit_logs.insert(0, {
        "id": f"log-{len(dbApplication.audit_logs) + 1}",
        "timestamp": datetime.now().isoformat(),
        "user_id": current_user.sub,
        "doctor_name": current_user.email,
        "action": "SOAP Temp Committed to SIMRS EMR",
        "details": f"Temp ID: {temp_id} | MRN: {mrn} | Log: {simrs_res.get('log_id')}",
        "tokens_used": 0,
        "status": "Success"
    })

    return TempSOAPCommitResponse(
        status="success",
        message=f"Catatan SOAP Temp berhasil dikirim dan disinkronisasikan ke SIMRS ({mrn}).",
        temp_soap=TempSOAPRecordSchema(**updated_rec),
        simrs_response=simrs_res
    )


@router.get("/soap-temp/{temp_id}/audio")
def stream_temp_soap_audio(
    temp_id: str,
    current_user: TokenPayload = Depends(require_role(["doctor", "admin"]))
):
    """Streams the recorded audio consultation file for a given temp SOAP."""
    rec = dbApplication.get_temp_soap(temp_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Data SOAP Temp tidak ditemukan.")
    if current_user.role != "admin" and rec["user_id"] != current_user.sub:
        raise HTTPException(status_code=403, detail="Akses ditolak.")

    audio_path = rec.get("audio_path")
    if not audio_path or not os.path.exists(audio_path):
        raise HTTPException(status_code=404, detail="Berkas rekaman audio tidak ditemukan di server.")

    media_type = "audio/wav" if rec["audio_filename"].lower().endswith(".wav") else "audio/mpeg"
    return FileResponse(
        path=audio_path,
        media_type=media_type,
        filename=rec.get("audio_filename", "recording.wav")
    )


@router.get("/soap-temp/audio-file/{filename}")
def stream_audio_file_by_name(filename: str):
    """Direct stream of stored audio recording for audio players."""
    # Sanitize filename
    safe_name = os.path.basename(filename)
    audio_path = os.path.join(AUDIO_STORAGE_DIR, safe_name)
    if not os.path.exists(audio_path):
        raise HTTPException(status_code=404, detail="Berkas audio tidak ditemukan.")

    media_type = "audio/wav" if safe_name.lower().endswith(".wav") else "audio/mpeg"
    return FileResponse(
        path=audio_path,
        media_type=media_type,
        filename=safe_name
    )




@router.put("/soa/review", response_model=SOAReviewResponse)
def review_soa_note(
    request: SOAReviewRequest,
    current_user: TokenPayload = Depends(require_role(["doctor", "admin"])),
):
    """Stage doctor edits and show the detected differences for explicit confirmation."""
    note = _get_owned_soa_note(request.note_id, current_user)
    proposed = request.model_dump(exclude={"note_id"})
    changes = [
        {"field": field, "previous": (note["content"].get(field) or ""), "proposed": (proposed.get(field) or "")}
        for field in ("subjective", "objective", "assessment", "plan")
        if (note["content"].get(field) or "").strip() != (proposed.get(field) or "").strip()
    ]
    if not changes:
        return SOAReviewResponse(
            note=_serialize_soa_note(note),
            message="Bot tidak menemukan perubahan pada resume S/O/A/P.",
        )

    note["pending_content"] = proposed
    note["changes"] = changes
    note["status"] = "pending_confirmation"
    note["updated_at"] = datetime.now().isoformat()
    message = (
        f"Saya mendeteksi {len(changes)} perubahan pada resume S/O/A. "
        "Tinjau perubahan berikut lalu konfirmasikan untuk menerima versi revisi."
    )
    session = dbApplication.chat_sessions.get(note["session_id"])
    if session:
        session["messages"].append({
            "role": "assistant",
            "content": message,
            "timestamp": datetime.now().isoformat(),
            "metadata": {"type": "soa_confirmation", "note_id": note["note_id"]},
        })
    dbApplication.audit_logs.insert(0, {
        "id": f"log-{len(dbApplication.audit_logs) + 1}",
        "timestamp": datetime.now().isoformat(),
        "user_id": current_user.sub,
        "doctor_name": current_user.email,
        "action": "S/O/A Resume Edit Submitted",
        "details": f"Note: {note['note_id']} | Proposed changes: {len(changes)}",
        "tokens_used": 0,
        "status": "Pending confirmation",
    })
    return SOAReviewResponse(note=_serialize_soa_note(note), message=message)


@router.put("/soa/confirmation", response_model=SOAReviewResponse)
def confirm_soa_note(
    request: SOAConfirmationRequest,
    current_user: TokenPayload = Depends(require_role(["doctor", "admin"])),
):
    """Accept or reject a staged S/O/A revision; acceptance is the only write action."""
    note = _get_owned_soa_note(request.note_id, current_user)
    if note["status"] != "pending_confirmation" or not note["pending_content"]:
        raise HTTPException(status_code=409, detail="Tidak ada revisi S/O/A yang menunggu konfirmasi.")

    if request.accept:
        note["content"] = note["pending_content"]
        note["status"] = "accepted"
        message = "Perubahan resume S/O/A telah dikonfirmasi dan versi revisi diterima."
        audit_action = "S/O/A Resume Revision Accepted"
    else:
        note["status"] = "draft"
        message = "Perubahan resume S/O/A ditolak. Versi sebelumnya tetap digunakan."
        audit_action = "S/O/A Resume Revision Rejected"
    note["pending_content"] = None
    note["changes"] = []
    note["updated_at"] = datetime.now().isoformat()
    session = dbApplication.chat_sessions.get(note["session_id"])
    if session:
        session["messages"].append({
            "role": "assistant",
            "content": message,
            "timestamp": datetime.now().isoformat(),
            "metadata": {"type": "soa_confirmation_result", "note_id": note["note_id"]},
        })
    dbApplication.audit_logs.insert(0, {
        "id": f"log-{len(dbApplication.audit_logs) + 1}",
        "timestamp": datetime.now().isoformat(),
        "user_id": current_user.sub,
        "doctor_name": current_user.email,
        "action": audit_action,
        "details": f"Note: {note['note_id']}",
        "tokens_used": 0,
        "status": "Success",
    })
    return SOAReviewResponse(note=_serialize_soa_note(note), message=message)


@router.get("/patients")
def get_available_patients(
    room_id: str | None = None,
    current_user: TokenPayload = Depends(require_role(["doctor", "admin"]))
):
    """Returns list of patient EHR summaries for doctor selection, optionally filtered by room/poli."""
    all_patients = list(dbApplication.patient_records.values())
    if room_id:
        matched = [p for p in all_patients if p.get("room_id") == room_id]
        return matched if matched else all_patients
    return all_patients


@router.get("/patients/lookup")
def lookup_patient(
    query: str,
    current_user: TokenPayload = Depends(require_role(["doctor", "admin"]))
):
    """Lookup patient in SIMRS by NIK, IHS Number, MRN ID, or Name."""
    q = query.strip().lower()
    if not q:
        raise HTTPException(status_code=400, detail="Parameter query pencarian pasien tidak boleh kosong.")

    for p in dbApplication.patient_records.values():
        p_id = (p.get("patient_id") or "").lower()
        nik = (p.get("nik") or "").lower()
        ihs = (p.get("ihs_number") or "").lower()
        name = (p.get("name") or "").lower()

        if q == p_id or q == nik or q == ihs or q in p_id or q in nik or q in ihs or q in name:
            return p

    raise HTTPException(status_code=404, detail=f"Data pasien dengan NIK/IHS/MRN '{query}' tidak ditemukan di SIMRS.")


@router.post("/chat/stream")
async def execute_agent_chat_stream(
    request: AgentChatRequest,
    current_user: TokenPayload = Depends(require_role(["doctor", "admin"]))
):
    """Server-Sent Events (SSE) endpoint to stream LangGraph steps and Gemini synthesis."""
    
    async def event_generator():
        initial_state = {
            "messages": [{"role": "user", "content": request.user_query}],
            "patient_id": request.patient_id,
            "user_query": request.user_query,
            "steps_executed": [],
            "ehr_data": None,
            "drug_interaction_findings": None,
            "literature_summary": None,
            "final_synthesis": ""
        }
        
        session_id = request.session_id or f"session-{int(datetime.now().timestamp())}"
        config = {"configurable": {"thread_id": session_id}}

        # Run graph with SQLite Checkpointer
        final_state = medical_agent_graph.invoke(initial_state, config=config)
        
        # Stream each step
        for step in final_state["steps_executed"]:
            yield f"data: {json.dumps({'event': 'step', 'step': step})}\n\n"
            await asyncio.sleep(0.4)
            
        # Stream final synthesis chunks
        synthesis = final_state["final_synthesis"]
        chunk_size = 40
        for i in range(0, len(synthesis), chunk_size):
            chunk = synthesis[i:i+chunk_size]
            yield f"data: {json.dumps({'event': 'chunk', 'text': chunk})}\n\n"
            await asyncio.sleep(0.05)
            
        if final_state.get("structured_output"):
            yield f"data: {json.dumps({'event': 'structured_output', 'structured_output': final_state['structured_output']})}\n\n"
            
        if final_state.get("output_validation"):
            yield f"data: {json.dumps({'event': 'output_validation', 'validation': final_state['output_validation']})}\n\n"

            
        session_id = request.session_id or f"session-{int(datetime.now().timestamp())}"
        yield f"data: {json.dumps({'event': 'completed', 'session_id': session_id})}\n\n"


    return StreamingResponse(event_generator(), media_type="text/event-stream")


# ── Clinic Room / Poli Selection Endpoints ──────────────────────────

@router.get("/clinic-rooms")
def list_clinic_rooms(current_user: TokenPayload = Depends(require_role(["doctor", "admin"]))):
    """Returns all available clinic rooms / poli for doctor room assignment."""
    return list(dbApplication.clinic_rooms.values())


@router.get("/clinic-rooms/selected")
def get_selected_room(current_user: TokenPayload = Depends(require_role(["doctor", "admin"]))):
    """Returns the doctor's currently selected room, or null if not set."""
    room_id = dbApplication.doctor_selected_room.get(current_user.sub)
    if not room_id:
        return {"selected_room": None}
    room = dbApplication.clinic_rooms.get(room_id)
    return {"selected_room": room}


@router.post("/clinic-rooms/select")
def select_clinic_room(
    payload: dict,
    current_user: TokenPayload = Depends(require_role(["doctor", "admin"]))
):
    """Set the doctor's active clinic room / poli."""
    room_id = payload.get("room_id", "")
    if room_id and room_id not in dbApplication.clinic_rooms:
        raise HTTPException(status_code=404, detail="Ruangan poli tidak ditemukan.")
    dbApplication.doctor_selected_room[current_user.sub] = room_id
    room = dbApplication.clinic_rooms.get(room_id)
    return {"status": "ok", "selected_room": room}

