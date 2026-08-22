from pydantic import BaseModel, Field
from typing import List, Optional

class GuardrailConfigSchema(BaseModel):
    enabled: bool = True
    pii_redaction_enabled: bool = True
    strictly_medical_scope: bool = True
    hallucination_prevention: bool = True
    toxic_content_filter: bool = True
    auto_disclaimer_enforced: bool = True
    min_confidence_score: float = Field(0.85, ge=0.0, le=1.0)
    max_query_length: int = Field(1500, ge=100, le=10000)
    banned_keywords: List[str] = Field(default_factory=list)
    allowed_domains: List[str] = Field(default_factory=list)
    safety_level: str = "Strict"
    updated_at: Optional[str] = None

class TestGuardrailRequest(BaseModel):
    text: str
    target_type: str = "input" # input | output

class TestGuardrailResponse(BaseModel):
    passed: bool
    verdict: str
    risk_score: float
    risk_level: str # Low | Medium | High | Critical
    violations: List[str]
    redacted_text: Optional[str] = None
    applied_rules: List[str]

class GuardrailViolationSchema(BaseModel):
    id: str
    timestamp: str
    user_id: str
    doctor_name: str
    query: str
    violated_rule: str
    action_taken: str
    risk_level: str
    verdict: str
