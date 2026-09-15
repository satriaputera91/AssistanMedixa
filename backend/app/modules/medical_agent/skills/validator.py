import logging
from typing import Dict, Any, Optional
from app.modules.medical_agent.context.state import MedicalAgentState
from app.modules.medical_agent.output_schemas import OutputValidator
from app.modules.medical_agent.logging_utils import log_node_start, log_node_end

def node_validate_output(state: MedicalAgentState) -> MedicalAgentState:
    """Validates generated clinical text for safety, allergy contraindications, and grounding with 3-round refinement loop."""
    current_iter = (state.get("iteration_count") or 0) + 1
    max_iter = state.get("max_iterations") or 3
    
    log_node_start(f"validate_output (Putaran {current_iter}/{max_iter})", state, icon="🛡️")
    query = state.get("user_query", "")
    patient_id = state.get("patient_id")
    final_text = state.get("final_synthesis", "")
    steps = list(state.get("steps_executed", []))
    
    ehr_data = state.get("ehr_data")
    simrs_profile = state.get("simrs_profile")
    simrs_history = state.get("simrs_history")
    simrs_anamnesis = state.get("simrs_anamnesis")
    simrs_labs = state.get("simrs_lab_evaluations")
    drug_safety = state.get("drug_safety_screening")

    validated_text, val_report = OutputValidator.validate_clinical_output(
        output_text=final_text,
        patient_id=patient_id,
        ehr_data=ehr_data,
        simrs_profile=simrs_profile,
        simrs_history=simrs_history,
        simrs_anamnesis=simrs_anamnesis,
        simrs_labs=simrs_labs,
        drug_safety=drug_safety,
        round_number=current_iter,
        max_rounds=max_iter
    )

    iteration_history = list(state.get("iteration_history") or [])
    iteration_history.append({
        "round": current_iter,
        "validation_score": val_report.validation_score,
        "status": val_report.status,
        "verdict": val_report.verdict,
        "alerts": val_report.alerts,
        "needs_refinement": val_report.needs_refinement,
        "refinement_feedback": val_report.refinement_feedback,
    })

    steps.append({
        "step_name": f"Validasi & Self-Reflection (Putaran {current_iter}/{max_iter})",
        "description": f"Verifikasi grounding klinis, kontraindikasi alergi, dan kepatuhan disclaimer. Skor: {val_report.validation_score}",
        "status": "success" if val_report.is_valid else "warning",
        "result": val_report.model_dump()
    })
    log_node_end(
        f"validate_output (Putaran {current_iter}/{max_iter})", 
        f"Score: {val_report.validation_score} | Verdict: {val_report.verdict} | Needs Refinement: {val_report.needs_refinement}"
    )

    return {
        **state,
        "iteration_count": current_iter,
        "max_iterations": max_iter,
        "refinement_feedback": val_report.refinement_feedback,
        "iteration_history": iteration_history,
        "steps_executed": steps,
        "final_synthesis": validated_text,
        "output_validation": val_report.model_dump()
    }
