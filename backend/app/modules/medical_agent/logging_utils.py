import logging
from typing import Optional, Any
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


def log_node_start(node_name: str, state: dict, icon: str = "▶️"):
    """Logs the entry into a LangGraph node with patient context and user query."""
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
    """Logs the completion of a LangGraph node with summary information."""
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
