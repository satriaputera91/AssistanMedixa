from pydantic import BaseModel, EmailStr
from typing import List, Optional

class CreateUserRequest(BaseModel):
    email: EmailStr
    name: str
    password: str
    role: str # "doctor" or "admin"
    specialty: Optional[str] = "General Medicine"
    license_no: Optional[str] = "MD-NEW"

class UserAdminView(BaseModel):
    id: str
    email: str
    name: str
    role: str
    specialty: Optional[str]
    license_no: Optional[str]
    is_active: bool
    created_at: str

class AuditLogItem(BaseModel):
    id: str
    timestamp: str
    user_id: str
    doctor_name: str
    action: str
    details: str
    tokens_used: int
    status: str

class AdminStatsResponse(BaseModel):
    total_doctors: int
    total_admins: int
    total_chat_sessions: int
    total_queries_run: int
    total_gemini_tokens: int
    gemini_model_active: str
    total_clinic_rooms: Optional[int] = 0


class UsageDailyPoint(BaseModel):
    date: str
    requests: int
    tokens: int


class UsageAnalyticsResponse(BaseModel):
    total_requests: int
    total_tokens: int
    average_tokens_per_request: int
    audio_requests: int
    soa_revisions: int
    requests_by_day: List[UsageDailyPoint]
    top_actions: List[dict]


class ServiceHealthSchema(BaseModel):
    name: str
    status: str
    detail: str


class MonitoringResponse(BaseModel):
    services: List[ServiceHealthSchema]
    checked_at: str


class AssignedDoctorView(BaseModel):
    id: str
    name: str
    email: str
    specialty: Optional[str] = None
    license_no: Optional[str] = None


class ClinicRoomAdminView(BaseModel):
    room_id: str
    room_name: str
    room_code: str
    floor: str
    building: str
    specialty: str
    status: str
    description: Optional[str] = None
    operational_hours: Optional[str] = "08:00 - 16:00 WIB"
    assigned_doctors: List[AssignedDoctorView] = []
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class CreateClinicRoomRequest(BaseModel):
    room_id: Optional[str] = None
    room_name: str
    room_code: str
    floor: str
    building: str
    specialty: str
    status: Optional[str] = "active"
    description: Optional[str] = None
    operational_hours: Optional[str] = "08:00 - 16:00 WIB"


class UpdateClinicRoomRequest(BaseModel):
    room_name: Optional[str] = None
    room_code: Optional[str] = None
    floor: Optional[str] = None
    building: Optional[str] = None
    specialty: Optional[str] = None
    status: Optional[str] = None
    description: Optional[str] = None
    operational_hours: Optional[str] = None

