import logging
from typing import Dict, Any, Optional
# pyrefly: ignore [missing-import]
from langgraph.graph import StateGraph, END

from app.modules.medical_agent.context.state import MedicalAgentState
from app.modules.medical_agent.memory.checkpointer import sqlite_checkpointer
from app.modules.medical_agent.agent.logging_utils import log_node_start, log_node_end, log_edge_transition
from app.modules.medical_agent.agent.planner import node_planner
from app.modules.medical_agent.agent.synthesis import node_gemini_synthesis
from app.modules.medical_agent.agent.validator import node_validate_output

from app.modules.medical_agent.skills.anamnesis import node_fetch_patient_history, node_fetch_patient_anamnesis
from app.modules.medical_agent.skills.diagnostics import node_eval_simrs_labs, node_diagnostic_recommendation
from app.modules.medical_agent.skills.disease_explanation import node_km_disease_explanations
from app.modules.medical_agent.skills.red_flags import node_km_red_flag_detection
from app.modules.medical_agent.skills.pharmacology import node_km_medication_recommendation, node_patient_drug_safety
from app.modules.medical_agent.skills.audio_soap import node_audio_transcription, node_audio_soap_summary

from app.core.database import dbApplication
from app.modules.medical_agent.tools.simrs_tools import tool_simrs_update_patient_record
from app.modules.medical_agent.tools.rag_tools import tool_vector_rag_search, tool_get_clinical_literature_summary

logger = logging.getLogger("medical_agent.agent.graph")

def node_execute_tools(state: MedicalAgentState) -> MedicalAgentState:
    """Executes SIMRS commit transactions, vector RAG search, and clinical literature lookup."""
    log_node_start("tools", state, icon="🛠️")
    query = state.get("user_query", "")
    query_lower = query.lower()
    patient_id = state.get("patient_id")
    steps = list(state.get("steps_executed", []))
    
    simrs_update_res = None
    drug_findings = list(state.get("drug_interaction_findings") or [])
    rag_chunks = []
    
    simrs_mrn = f"MRN-SIMRS-{patient_id.replace('P-', '')}" if (patient_id and patient_id.strip()) else None

    # Step 3A: SIMRS CPPT Commit Transaction if requested (Uses Temp SOAP if available)
    if simrs_mrn and any(k in query_lower for k in ["buat cppt", "kirim cppt", "kirim soap", "buat soap", "sinkronisasi cppt", "simpan cppt", "kirim/sinkronisasikan", "update simrs", "sync simrs", "commit emr", "kirim ke simrs", "kirim/sinkronisasi"]):
        # 1. Check if there is an existing temporary SOAP record in application database
        temp_rec = None
        if patient_id:
            temp_list = dbApplication.list_temp_soap(patient_id=patient_id, limit=1)
            if temp_list:
                temp_rec = temp_list[0]

        if temp_rec and temp_rec.get("soap_content"):
            sc = temp_rec["soap_content"]
            chief = sc.get("subjective", "Keluhan klinis terkontrol")
            objective_val = sc.get("objective", "Tanda vital dan lab dalam batas evaluasi")
            primary_dx = sc.get("assessment", "Evaluasi Klinis Terintegrasi")
            treatment_plan = sc.get("plan", "Lanjutkan terapi farmakologi dan monitoring serial.")
            if sc.get("instructions"):
                treatment_plan += f" | Instruksi: {sc.get('instructions')}"
            doctor_notes = f"S: {chief}\nO: {objective_val}\nA: {primary_dx}\nP: {treatment_plan}"
            source_desc = f"Data bersumber dari SOAP Temp ({temp_rec['temp_id']})"
        else:
            anamnesis = state.get("simrs_anamnesis") or {}
            labs = state.get("simrs_lab_evaluations") or {}
            diag = state.get("diagnostic_recommendations") or {}
            med = state.get("medication_recommendations") or {}

            primary_dx = "Evaluasi Klinis Terintegrasi"
            if diag.get("primary_recommendations"):
                d = diag["primary_recommendations"][0]
                primary_dx = f"{d['diagnosis']} [ICD-10: {d['icd10']}]"

            treatment_plan = "Lanjutkan terapi farmakologi dan monitoring serial."
            if med.get("recommended_regimens") and isinstance(med["recommended_regimens"], list):
                treatment_plan = ", ".join([f"{m.get('drug_name', '')} ({m.get('class', '')})" for m in med["recommended_regimens"][:2]])
            
            chief = anamnesis.get("chief_complaint", "Keluhan klinis terkontrol")
            vitals = labs.get("vital_signs", {})
            tensi = vitals.get("blood_pressure", "120/80 mmHg")
            hr = vitals.get("heart_rate", "80 bpm")
            doctor_notes = f"S: {chief} | O: BP {tensi}, HR {hr}, Suhu {vitals.get('temperature', '36.8°C')} | A: {primary_dx} | P: {treatment_plan}"
            source_desc = "Data bersumber dari modul anamnesis & lab RME SIMRS"

        update_res = tool_simrs_update_patient_record(
            mrn=simrs_mrn,
            doctor_notes=doctor_notes,
            primary_diagnosis=primary_dx,
            treatment_plan=treatment_plan
        )
        simrs_update_res = update_res

        # Mark temp soap synced if present
        if temp_rec and update_res.get("status") == "success":
            dbApplication.mark_temp_soap_synced(temp_rec["temp_id"], update_res)

        steps.append({
            "step_name": "Sinkronisasi & Commit CPPT ke SIMRS (MCP)",
            "description": f"Menyimpan resume CPPT S/O/A/P terintegrasi ({source_desc}) ke dalam basis data RME SIMRS untuk MRN {simrs_mrn}",
            "status": "success",
            "result": {
                "log_id": update_res.get("log_id"),
                "mrn": simrs_mrn,
                "status": update_res.get("message"),
                "temp_soap_id": temp_rec.get("temp_id") if temp_rec else None,
                "waktu_sinkronisasi": update_res.get("timestamp")
            }
        })

    # Step 3B: Qdrant Vector RAG Search
    rag_search_query = query
    if state.get("simrs_anamnesis"):
        chief = state["simrs_anamnesis"].get("chief_complaint", "")
        rps = state["simrs_anamnesis"].get("history_present_illness", "")
        rag_search_query = f"{query} {chief} {rps}".strip()
    elif state.get("medication_recommendations"):
        disease = state["medication_recommendations"].get("disease", "")
        rag_search_query = f"{query} {disease}".strip()

    rag_res = tool_vector_rag_search(rag_search_query, top_k=3)
    if rag_res and isinstance(rag_res, list):
        rag_chunks = rag_res
        score_info = ", ".join([f"{c.get('title', 'Ref')} (Score: {c.get('reranked_score', c.get('score', 0.85))})" for c in rag_chunks])
        steps.append({
            "step_name": "Retrieval Augmenation Generation",
            "description": "Pencarian semantik vektor Qdrant + validasi relevansi klinis.",
            "status": "success",
            "result": f"Retrieved {len(rag_chunks)} top chunks: {score_info}"
        })

    # Step 3C: Clinical Literature Guidelines Summary
    lit_summary = tool_get_clinical_literature_summary(rag_search_query)
    steps.append({
        "step_name": "Evidence-Based Literature Search",
        "description": "Konsultasi pedoman praktik klinis berbasis bukti (KDIGO / ADA / ACC / PERKENI).",
        "status": "success",
        "result": lit_summary[:120] + "..." if lit_summary else "Panduan klinis tersedia."
    })

    log_node_end("tools", f"RAG Chunks: {len(rag_chunks)} | Literature: {len(lit_summary)} chars | SIMRS Commit: {bool(simrs_update_res)}")
    return {
        **state,
        "steps_executed": steps,
        "simrs_update_res": simrs_update_res,
        "drug_interaction_findings": drug_findings,
        "literature_summary": lit_summary,
        "rag_chunks": rag_chunks
    }


def _route_entry_point(state: MedicalAgentState) -> str:
    """Routes initial request based on whether audio bytes are provided."""
    workflow_type = state.get("workflow_type")
    audio_bytes = state.get("audio_bytes")
    if workflow_type == "audio" or audio_bytes:
        log_edge_transition("START", "audio_transcription", condition="workflow_type == 'audio'")
        return "audio_transcription"
    log_edge_transition("START", "planner", condition="workflow_type != 'audio' or text query")
    return "planner"


def _route_planner(state: MedicalAgentState) -> str:
    """Determines whether to execute patient EMR retrieval nodes or bypass directly to tools/synthesis."""
    patient_id = state.get("patient_id")
    detected_intent = state.get("detected_intent")

    if not patient_id or not patient_id.strip():
        if detected_intent is None:
            log_edge_transition("planner", "synthesis", condition="general consultation: no intent -> direct to synthesis")
            return "synthesis"
        log_edge_transition("planner", "tools", condition="general consultation: bypass all SIMRS read nodes -> direct to tools (RAG/KM)")
        return "tools"

    if detected_intent is None:
        log_edge_transition("planner", "synthesis", condition="no clinical intent detected (skip workflow nodes)")
        return "synthesis"
    else:
        log_edge_transition("planner", "fetch_patient_history", condition=f"patient mode ({patient_id}): read SIMRS EMR workflow")
        return "fetch_patient_history"


def build_medical_agent_graph(checkpointer=None):
    """Builds and compiles the Medical Agent LangGraph StateGraph."""
    workflow = StateGraph(MedicalAgentState)
    
    # Register Nodes
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
    
    # Conditional Entry Point
    workflow.set_conditional_entry_point(
        _route_entry_point,
        {"audio_transcription": "audio_transcription", "planner": "planner"},
    )
    
    # Audio Sub-Workflow
    workflow.add_edge("audio_transcription", "audio_soap_summary")
    workflow.add_edge("audio_soap_summary", "validate_output")
    
    # Text Consultation Workflow
    workflow.add_conditional_edges(
        "planner",
        _route_planner,
        {
            "synthesis": "synthesis",
            "tools": "tools",
            "fetch_patient_history": "fetch_patient_history",
        },
    )
    
    # Patient Workflow Pipeline
    workflow.add_edge("fetch_patient_history", "fetch_patient_anamnesis")
    workflow.add_edge("fetch_patient_anamnesis", "eval_simrs_labs")
    workflow.add_edge("eval_simrs_labs", "diagnostic_recommendation")
    workflow.add_edge("diagnostic_recommendation", "km_disease_explanations")
    workflow.add_edge("km_disease_explanations", "km_red_flag_detection")
    workflow.add_edge("km_red_flag_detection", "km_medication_recommendation")
    workflow.add_edge("km_medication_recommendation", "patient_drug_safety")
    workflow.add_edge("patient_drug_safety", "tools")
    
    # Core Synthesis & Validation Loop
    workflow.add_edge("tools", "synthesis")
    workflow.add_edge("synthesis", "validate_output")
    workflow.add_edge("validate_output", END)
    
    cp = checkpointer if checkpointer is not None else sqlite_checkpointer
    return workflow.compile(checkpointer=cp)


medical_agent_graph = build_medical_agent_graph()
