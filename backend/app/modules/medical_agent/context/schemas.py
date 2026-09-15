# pyrefly: ignore [missing-import]
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class AgentChatRequest(BaseModel):
    user_query: str
    patient_id: Optional[str] = None
    session_id: Optional[str] = None

class AgentStepSchema(BaseModel):
    step_name: str
    description: str
    status: str
    result: Optional[Any] = None

class OutputValidationSchema(BaseModel):
    is_valid: bool = True
    status: str = "PASSED"
    verdict: str = "VALID"
    validation_score: float = 1.0
    alerts: List[str] = Field(default_factory=list)
    remediation_applied: bool = False
    details: Optional[Dict[str, Any]] = None
    timestamp: Optional[str] = None

class SOAContentSchema(BaseModel):
    subjective: str = ""
    objective: str = ""
    assessment: str = ""
    plan: Optional[str] = ""

SOAPContentSchema = SOAContentSchema

class SOAChangeSchema(BaseModel):
    field: str
    previous: str
    proposed: str

class SOANoteSchema(BaseModel):
    note_id: str
    session_id: str
    content: SOAContentSchema
    status: str
    pending_content: Optional[SOAContentSchema] = None
    changes: List[SOAChangeSchema] = Field(default_factory=list)
    updated_at: str

class SOAReviewRequest(SOAContentSchema):
    note_id: str

class SOAReviewResponse(BaseModel):
    note: SOANoteSchema
    message: str

class SOAConfirmationRequest(BaseModel):
    note_id: str
    accept: bool

class SOARevisionConfirmationRequest(BaseModel):
    session_id: str
    accepted: bool
    doctor_comments: Optional[str] = None

class TempSOAPContentSchema(BaseModel):
    subjective: str = ""
    objective: str = ""
    assessment: str = ""
    plan: Optional[str] = ""
    instructions: Optional[str] = ""

class TempSOAPRecordSchema(BaseModel):
    temp_id: str
    session_id: str
    patient_id: Optional[str] = None
    patient_name: Optional[str] = None
    mrn: Optional[str] = None
    nik: Optional[str] = None
    user_id: str
    doctor_name: str
    audio_filename: str
    audio_url: str
    audio_path: Optional[str] = None
    audio_size_bytes: int = 0
    audio_transcript: str = ""
    soap_content: TempSOAPContentSchema
    raw_markdown: str = ""
    structured_output: Optional[Dict[str, Any]] = None
    status: str = "draft"
    simrs_sync_status: str = "pending"
    simrs_log_id: Optional[str] = None
    simrs_response: Optional[Dict[str, Any]] = None
    created_at: str
    updated_at: str
    synced_at: Optional[str] = None

class TempSOAPUpdateRequest(BaseModel):
    soap_content: Optional[TempSOAPContentSchema] = None
    raw_markdown: Optional[str] = None
    status: Optional[str] = None

class CreateManualTempSOAPRequest(BaseModel):
    session_id: str
    patient_id: Optional[str] = None
    soap_content: TempSOAPContentSchema
    raw_markdown: Optional[str] = None
    structured_output: Optional[Dict[str, Any]] = None

class HITLOptionSchema(BaseModel):
    key: str
    label: str
    icon: str
    description: str
    action_type: str  # "record_audio" | "upload_file" | "manual_modal"

class HITLDataSchema(BaseModel):
    required: bool = True
    type: str = "missing_subjective_objective"
    title: str = "Mohon maaf hasil anamnesis atau pemeriksaan belum disampaikan, Silahkan isi terlebih dahulu?"
    options: List[HITLOptionSchema] = Field(default_factory=list)

class TempSOAPCommitResponse(BaseModel):
    status: str
    message: str
    temp_soap: TempSOAPRecordSchema
    simrs_response: Optional[Dict[str, Any]] = None

class AgentChatResponse(BaseModel):
    session_id: str
    user_query: str
    patient_id: Optional[str]
    steps_executed: List[AgentStepSchema]
    final_synthesis: str
    workflow_type: Optional[str] = None
    audio_transcript: Optional[str] = None
    soa_note: Optional[SOANoteSchema] = None
    temp_soap: Optional[TempSOAPRecordSchema] = None
    output_validation: Optional[OutputValidationSchema] = None
    structured_output: Optional[Dict[str, Any]] = None
    hitl_required: Optional[bool] = False
    hitl_data: Optional[Dict[str, Any]] = None
