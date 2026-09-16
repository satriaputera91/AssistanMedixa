import logging
import queue
from datetime import datetime
from typing import Optional, Any, Dict
from contextvars import ContextVar
from app.core.database import db

# Setup standard structured logger
logger = logging.getLogger("medical_agent")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-7s | [%(filename)s:%(lineno)d] | %(funcName)s() | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Realtime status event queue context
_status_queue_ctx: ContextVar[Optional[queue.Queue]] = ContextVar("status_queue_ctx", default=None)

NODE_DISPLAY_MAP: Dict[str, Dict[str, str]] = {
    "planner": {"label": "Planner", "icon": "🧠", "desc": "Menganalisis kueri & klasifikasi alur klinis..."},
    "fetch_patient_history": {"label": "SIMRS EMR", "icon": "👤", "desc": "Membaca rekam medis terintegrasi SIMRS..."},
    "fetch_patient_anamnesis": {"label": "Anamnesis", "icon": "📝", "desc": "Mengevaluasi riwayat dan keluhan klinis..."},
    "eval_simrs_labs": {"label": "Lab & Vitals", "icon": "🧪", "desc": "Menganalisis hasil laboratorium & tanda vital..."},
    "diagnostic_recommendation": {"label": "Diagnosis", "icon": "🎯", "desc": "Menyusun diagnosis kerja & ICD-10..."},
    "km_disease_explanations": {"label": "Knowledge", "icon": "📚", "desc": "Meninjau panduan klinis & patofisiologi..."},
    "km_red_flag_detection": {"label": "Red Flag", "icon": "🚨", "desc": "Memeriksa tanda bahaya & kedaruratan medis..."},
    "km_medication_recommendation": {"label": "Medication", "icon": "💊", "desc": "Menentukan rekomendasi obat & dosis..."},
    "patient_drug_safety": {"label": "Drug Safety", "icon": "🛡️", "desc": "Skrining interaksi obat & keamanan alergi..."},
    "tools": {"label": "MCP & RAG", "icon": "🛠️", "desc": "Menjalankan pencarian RAG & transaksi SIMRS..."},
    "synthesis": {"label": "Synthesis", "icon": "🩺", "desc": "Menyusun penalaran klinis komprehensif & resume SOAP..."},
    "validate_output": {"label": "Guardrails", "icon": "🛡️", "desc": "Memverifikasi kepatuhan disclaimer & guardrails medis..."},
    "audio_transcription": {"label": "Transkripsi", "icon": "🎙️", "desc": "Memproses transkripsi rekaman audio konsultasi..."},
    "audio_soap_summary": {"label": "SOAP Audio", "icon": "📋", "desc": "Mengekstrak resume SOAP dari transkrip audio..."},
}


def register_status_queue(q: queue.Queue):
    """Registers a status queue for the current context."""
    return _status_queue_ctx.set(q)


def unregister_status_queue(token):
    """Unregisters the status queue."""
    try:
        _status_queue_ctx.reset(token)
    except Exception:
        pass


def emit_workflow_status(event_data: dict):
    """Puts a status event into the active request status queue if registered."""
    q = _status_queue_ctx.get()
    if q is not None:
        try:
            q.put(event_data, block=False)
        except Exception:
            pass


def log_node_start(node_name: str, state: dict, icon: str = "▶️"):
    """Logs the entry into a LangGraph node with patient context and user query, and emits realtime status."""
    raw_key = node_name.split()[0]
    display = NODE_DISPLAY_MAP.get(raw_key, {"label": raw_key, "icon": icon, "desc": f"Memproses node {raw_key}..."})

    # Instantly emit realtime node_started event
    emit_workflow_status({
        "status": "running",
        "phase": "node_started",
        "node_name": raw_key,
        "label": display["label"],
        "icon": display["icon"],
        "summary": display.get("desc", f"Sedang memproses {display['label']}..."),
        "timestamp": datetime.now().isoformat()
    })

    patient_id = state.get("patient_id") or "N/A"
    patient_name = None
    if patient_id and patient_id != "N/A":
        try:
            p_rec = db.patient_records.get(patient_id)
            if p_rec:
                patient_name = p_rec.get("name")
        except Exception:
            pass
    pat_str = f"{patient_id} ({patient_name})" if patient_name else patient_id
    query_str = (state.get("user_query") or "")[:70]
    logger.info(
        f"{icon} [LANGGRAPH NODE START] >>> {node_name} | Patient: {pat_str} | Query: '{query_str}'",
        stacklevel=2
    )


def log_node_end(node_name: str, message: str, icon: str = "✅"):
    """Logs the completion of a LangGraph node with summary information, and emits realtime completion event."""
    raw_key = node_name.split()[0]
    display = NODE_DISPLAY_MAP.get(raw_key, {"label": raw_key, "icon": icon, "desc": message})

    emit_workflow_status({
        "status": "node_completed",
        "node_name": raw_key,
        "label": display["label"],
        "icon": display["icon"],
        "summary": message,
        "timestamp": datetime.now().isoformat()
    })

    logger.info(
        f"{icon} [LANGGRAPH NODE COMPLETED] <<< {node_name} | {message}",
        stacklevel=2
    )


def log_edge_transition(source: str, target: str, condition: str = ""):
    """Logs the edge transition between LangGraph nodes with decision rationale."""
    cond_str = f" (Condition: {condition})" if condition else ""
    logger.info(
        f"🔀 [LANGGRAPH EDGE TRANSITION] {source} ──▶ {target}{cond_str}",
        stacklevel=2
    )


# Backward compatibility aliases
_debug_node_start = log_node_start
_debug_node_end = log_node_end
_debug_edge = log_edge_transition
