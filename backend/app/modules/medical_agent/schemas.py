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

class AgentChatResponse(BaseModel):
    session_id: str
    user_query: str
    patient_id: Optional[str]
    steps_executed: List[AgentStepSchema]
    final_synthesis: str
    workflow_type: Optional[str] = None
    audio_transcript: Optional[str] = None
    soa_note: Optional["SOANoteSchema"] = None


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
