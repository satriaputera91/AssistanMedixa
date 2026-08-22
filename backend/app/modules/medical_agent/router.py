import json
import asyncio
import re
from uuid import uuid4
from datetime import datetime
# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
# pyrefly: ignore [missing-import]
from fastapi.responses import StreamingResponse
from app.core.security import get_current_user, TokenPayload, require_role
from app.core.database import db
from app.core.config import settings
from app.modules.medical_agent.schemas import (
    AgentChatRequest, AgentChatResponse, SOAContentSchema, SOANoteSchema,
    SOAReviewRequest, SOAReviewResponse, SOAConfirmationRequest,
)
from app.modules.medical_agent.agent_graph import medical_agent_graph

router = APIRouter(prefix="/agent", tags=["Medical Agent"])


def _soap_section(markdown: str, heading: str) -> str:
    first_letter = heading[0].upper()
    # Match headers like ### S — Subjective, ### S - Subjective, ### P — Plan, ## Subjective, etc.
    pattern = rf"(?:###|\*\*|##)\s*(?:[👤🔬🎯💊📝]\s*)?(?:{first_letter}\s*[—\-\(:\.]\s*{heading}|{heading})[^\n]*\n(.*?)(?=(?:###|\*\*|##)\s*(?:[👤🔬🎯💊📝]\s*)?(?:[SOAPI]\s*[—\-\(:\.]|Subjective|Objective|Assessment|Plan|Instruksi|Transkrip|---\n|\*\(⚠️|\Z))"
    match = re.search(pattern, markdown, flags=re.IGNORECASE | re.MULTILINE | re.DOTALL)
    if match and match.group(1).strip():
        return match.group(1).strip()
    pattern2 = rf"^##\s+(?:[{first_letter}]\s*[—-]\s*)?{heading}\s*$\s*(.*?)(?=^##\s|\Z)"
    match2 = re.search(pattern2, markdown, flags=re.IGNORECASE | re.MULTILINE | re.DOTALL)
    return match2.group(1).strip() if match2 else "Tidak disebutkan."


_soa_section = _soap_section


def _create_soap_note(final_synthesis: str, session_id: str, user_id: str) -> dict:
    now = datetime.now().isoformat()
    note = {
        "note_id": f"soap-{uuid4().hex}",
        "session_id": session_id,
        "user_id": user_id,
        "content": {
            "subjective": _soap_section(final_synthesis, "Subjective"),
            "objective": _soap_section(final_synthesis, "Objective"),
            "assessment": _soap_section(final_synthesis, "Assessment"),
            "plan": _soap_section(final_synthesis, "Plan"),
        },
        "status": "draft",
        "pending_content": None,
        "changes": [],
        "updated_at": now,
    }
    db.soa_notes[note["note_id"]] = note
    return note


_create_soa_note = _create_soap_note


def _serialize_soa_note(note: dict) -> SOANoteSchema:
    return SOANoteSchema(**note)


def _get_owned_soa_note(note_id: str, current_user: TokenPayload) -> dict:
    note = db.soa_notes.get(note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Resume S/O/A tidak ditemukan.")
    if current_user.role != "admin" and note["user_id"] != current_user.sub:
        raise HTTPException(status_code=403, detail="Forbidden access to S/O/A resume")
    return note

@router.post("/chat", response_model=AgentChatResponse)
def execute_agent_chat(
    request: AgentChatRequest,
    current_user: TokenPayload = Depends(require_role(["doctor", "admin"]))
):
    initial_state = {
        "messages": [{"role": "user", "content": request.user_query}],
        "patient_id": request.patient_id,
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
    session_id = request.session_id or f"session-{int(datetime.now().timestamp())}"
    turn_thread_id = f"{session_id}-turn-{int(datetime.now().timestamp() * 1000)}"
    config = {"configurable": {"thread_id": turn_thread_id}}

    # Run LangGraph StateGraph with isolated memory per chat turn
    final_state = medical_agent_graph.invoke(initial_state, config=config)
    
    # Update DB session & history
    doctor_name = current_user.email
    user_rec = db.users.get(current_user.sub)
    if user_rec:
        doctor_name = user_rec["name"]
        
    if session_id not in db.chat_sessions:
        db.chat_sessions[session_id] = {
            "session_id": session_id,
            "user_id": current_user.sub,
            "title": request.user_query[:40] + ("..." if len(request.user_query) > 40 else ""),
            "created_at": datetime.now().isoformat(),
            "patient_id": request.patient_id,
            "messages": []
        }
        
    db.chat_sessions[session_id]["messages"].append({
        "role": "user",
        "content": request.user_query,
        "timestamp": datetime.now().isoformat()
    })
    db.chat_sessions[session_id]["messages"].append({
        "role": "assistant",
        "content": final_state["final_synthesis"],
        "timestamp": datetime.now().isoformat(),
        "metadata": {
            "steps": final_state.get("steps_executed", [])
        }
    })
    
    # Log action in audit trail
    db.audit_logs.insert(0, {
        "id": f"log-{len(db.audit_logs)+1}",
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
    """Process a WAV or MP3 recording through Gemini STT with Speaker Diarization, then produce structured SOAP summary."""
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

    if resolved_session_id not in db.chat_sessions:
        db.chat_sessions[resolved_session_id] = {
            "session_id": resolved_session_id,
            "user_id": current_user.sub,
            "title": f"Audio: {filename}"[:40],
            "created_at": datetime.now().isoformat(),
            "patient_id": patient_id,
            "messages": [],
        }
    elif current_user.role != "admin" and db.chat_sessions[resolved_session_id]["user_id"] != current_user.sub:
        raise HTTPException(status_code=403, detail="Forbidden access to chat session")

    soa_note = None
    if final_state.get("audio_transcript") and not final_state.get("audio_error"):
        soa_note = _create_soap_note(final_state["final_synthesis"], resolved_session_id, current_user.sub)

    db.chat_sessions[resolved_session_id]["messages"].extend([
        {"role": "user", "content": audio_label, "timestamp": datetime.now().isoformat()},
        {
            "role": "assistant",
            "content": final_state["final_synthesis"],
            "timestamp": datetime.now().isoformat(),
            "metadata": {
                "type": "soa_note" if soa_note else None,
                "note": soa_note,
                "steps": final_state.get("steps_executed", []),
            },
        },
    ])
    db.audit_logs.insert(0, {
        "id": f"log-{len(db.audit_logs) + 1}",
        "timestamp": datetime.now().isoformat(),
        "user_id": current_user.sub,
        "doctor_name": current_user.email,
        "action": "Gemini Audio STT & S/O/A/P Summary",
        "details": f"Audio: '{filename}' | Patient: {patient_id or 'N/A'}",
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
        output_validation=final_state.get("output_validation"),
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
    session = db.chat_sessions.get(note["session_id"])
    if session:
        session["messages"].append({
            "role": "assistant",
            "content": message,
            "timestamp": datetime.now().isoformat(),
            "metadata": {"type": "soa_confirmation", "note_id": note["note_id"]},
        })
    db.audit_logs.insert(0, {
        "id": f"log-{len(db.audit_logs) + 1}",
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
    session = db.chat_sessions.get(note["session_id"])
    if session:
        session["messages"].append({
            "role": "assistant",
            "content": message,
            "timestamp": datetime.now().isoformat(),
            "metadata": {"type": "soa_confirmation_result", "note_id": note["note_id"]},
        })
    db.audit_logs.insert(0, {
        "id": f"log-{len(db.audit_logs) + 1}",
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
    all_patients = list(db.patient_records.values())
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

    for p in db.patient_records.values():
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
            
        if final_state.get("output_validation"):
            yield f"data: {json.dumps({'event': 'output_validation', 'validation': final_state['output_validation']})}\n\n"
            
        session_id = request.session_id or f"session-{int(datetime.now().timestamp())}"
        yield f"data: {json.dumps({'event': 'completed', 'session_id': session_id})}\n\n"


    return StreamingResponse(event_generator(), media_type="text/event-stream")


# ── Clinic Room / Poli Selection Endpoints ──────────────────────────

@router.get("/clinic-rooms")
def list_clinic_rooms(current_user: TokenPayload = Depends(require_role(["doctor", "admin"]))):
    """Returns all available clinic rooms / poli for doctor room assignment."""
    return list(db.clinic_rooms.values())


@router.get("/clinic-rooms/selected")
def get_selected_room(current_user: TokenPayload = Depends(require_role(["doctor", "admin"]))):
    """Returns the doctor's currently selected room, or null if not set."""
    room_id = db.doctor_selected_room.get(current_user.sub)
    if not room_id:
        return {"selected_room": None}
    room = db.clinic_rooms.get(room_id)
    return {"selected_room": room}


@router.post("/clinic-rooms/select")
def select_clinic_room(
    payload: dict,
    current_user: TokenPayload = Depends(require_role(["doctor", "admin"]))
):
    """Set the doctor's active clinic room / poli."""
    room_id = payload.get("room_id", "")
    if room_id and room_id not in db.clinic_rooms:
        raise HTTPException(status_code=404, detail="Ruangan poli tidak ditemukan.")
    db.doctor_selected_room[current_user.sub] = room_id
    room = db.clinic_rooms.get(room_id)
    return {"status": "ok", "selected_room": room}

