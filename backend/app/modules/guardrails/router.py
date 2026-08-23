from fastapi import APIRouter, Depends, HTTPException
from typing import List
from datetime import datetime
from app.core.security import TokenPayload, require_role
from app.core.database import db
from app.modules.guardrails.schemas import (
    GuardrailConfigSchema,
    TestGuardrailRequest,
    TestGuardrailResponse,
    GuardrailViolationSchema,
    ValidateOutputRequest,
)
from app.modules.guardrails.service import GuardrailsService
from app.modules.guardrails.output_validator import LLMOutputValidator


router = APIRouter(prefix="/guardrails", tags=["AI Safety & Guardrails"])

@router.get("/config", response_model=GuardrailConfigSchema)
def get_guardrail_config(current_user: TokenPayload = Depends(require_role(["admin"]))):
    """Retrieve current AI Guardrail safety configurations (Admin Only)."""
    return db.guardrail_config

@router.put("/config", response_model=GuardrailConfigSchema)
def update_guardrail_config(
    new_config: GuardrailConfigSchema,
    current_user: TokenPayload = Depends(require_role(["admin"]))
):
    """Update AI Guardrail parameters and security thresholds (Admin Only)."""
    config_dict = new_config.model_dump()
    config_dict["updated_at"] = datetime.now().isoformat()
    db.guardrail_config = config_dict
    
    db.audit_logs.insert(0, {
        "id": f"log-{len(db.audit_logs)+1}",
        "timestamp": datetime.now().isoformat(),
        "user_id": current_user.sub,
        "doctor_name": current_user.email,
        "action": "Guardrail Policies Updated",
        "details": f"Safety Level: {new_config.safety_level} | Enabled: {new_config.enabled}",
        "tokens_used": 0,
        "status": "Success"
    })
    
    return db.guardrail_config

@router.post("/test", response_model=TestGuardrailResponse)
def test_guardrails(
    request: TestGuardrailRequest,
    current_user: TokenPayload = Depends(require_role(["admin", "doctor"]))
):
    """Live interactive testing tool to simulate guardrail evaluation against input or output text."""
    evaluation = GuardrailsService.evaluate(request.text, db.guardrail_config, request.target_type)
    
    # If severe violation, record into violation logs
    if not evaluation.passed:
        user_name = current_user.email
        user_rec = db.users.get(current_user.sub)
        if user_rec:
            user_name = user_rec["name"]

        db.guardrail_violations.insert(0, {
            "id": f"gr-log-{len(db.guardrail_violations)+1}",
            "timestamp": datetime.now().isoformat(),
            "user_id": current_user.sub,
            "doctor_name": user_name,
            "query": request.text[:80] + ("..." if len(request.text) > 80 else ""),
            "violated_rule": ", ".join(evaluation.violations) if evaluation.violations else "Safety Threshold Exceeded",
            "action_taken": "Blocked & Logged",
            "risk_level": evaluation.risk_level,
            "verdict": evaluation.verdict
        })
        
    return evaluation

@router.post("/validate-output")
def validate_clinical_output(
    request: ValidateOutputRequest,
    current_user: TokenPayload = Depends(require_role(["admin", "doctor"]))
):
    """
    Comprehensive live testing endpoint for validating LLM clinical output.
    Evaluates grounding, allergy contraindications, red flag coverage, and disclaimers.
    """
    simrs_anamnesis = {"allergy_history": request.allergies} if request.allergies else None
    red_flag_detections = {"detected_red_flags": [{"title": rf} for rf in request.red_flags]} if request.red_flags else None

    result = LLMOutputValidator.evaluate_all(
        output_text=request.text,
        simrs_anamnesis=simrs_anamnesis,
        red_flag_detections=red_flag_detections,
        config=db.guardrail_config
    )
    return result

@router.get("/violations", response_model=List[GuardrailViolationSchema])

def list_guardrail_violations(current_user: TokenPayload = Depends(require_role(["admin"]))):
    """List historical audit logs of blocked queries and safety violations (Admin Only)."""
    return db.guardrail_violations

@router.delete("/violations/{violation_id}")
def clear_guardrail_violation(
    violation_id: str,
    current_user: TokenPayload = Depends(require_role(["admin"]))
):
    """Clear specific violation audit record."""
    initial_len = len(db.guardrail_violations)
    db.guardrail_violations = [v for v in db.guardrail_violations if v["id"] != violation_id]
    if len(db.guardrail_violations) == initial_len:
        raise HTTPException(status_code=404, detail="Violation record not found")
    return {"status": "success", "cleared_id": violation_id}
