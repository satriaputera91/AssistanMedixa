from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class ChatMessageSchema(BaseModel):
    role: str
    content: str
    timestamp: str
    metadata: Optional[Dict[str, Any]] = None

class ChatSessionSchema(BaseModel):
    session_id: str
    user_id: str
    title: str
    created_at: str
    patient_id: Optional[str] = None
    temp_soap_id: Optional[str] = None
    temp_soap: Optional[Dict[str, Any]] = None
    messages: List[ChatMessageSchema]

class CreateSessionRequest(BaseModel):
    title: str
    patient_id: Optional[str] = None

class RenameSessionRequest(BaseModel):
    title: str

