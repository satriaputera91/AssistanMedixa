import logging
from typing import Dict, Any, Optional
from app.modules.medical_agent.context.state import MedicalAgentState
from app.modules.medical_agent.skills.output_schemas import OutputValidator

logger = logging.getLogger("medical_agent.agent.validator")

def node_validate_output(state: MedicalAgentState) -> MedicalAgentState:
    """Validates generated clinical text for safety, allergy contraindications, and grounding."""
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
        drug_safety=drug_safety
    )

    steps.append({
        "step_name": "Validasi Output LLM & Grounding Verifier",
        "description": f"Verifikasi grounding klinis, kontraindikasi alergi, dan kepatuhan disclaimer. Skor: {val_report.validation_score}",
        "status": "success" if val_report.is_valid else "warning",
        "result": val_report.model_dump()
    })

    return {
        **state,
        "steps_executed": steps,
        "final_synthesis": validated_text,
        "output_validation": val_report.model_dump()
    }
