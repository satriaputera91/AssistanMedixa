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


# ── MCP Dynamic Configuration & Tool Schemas ───────────────────────

class MCPConfigSchema(BaseModel):
    server_name: str
    protocol_version: str
    mode: str # "mock" | "live" | "hybrid"
    endpoint_url: str
    auth_type: str # "bearer" | "api_key" | "none"
    auth_token: Optional[str] = ""
    timeout_seconds: int = 10
    retry_attempts: int = 3
    enable_audit_logging: bool = True
    auto_sync_enabled: bool = True
    custom_headers: Optional[dict] = {}
    status: str = "connected"
    latency_ms: Optional[int] = 12
    last_health_check: Optional[str] = None
    updated_at: Optional[str] = None


class UpdateMCPConfigRequest(BaseModel):
    server_name: Optional[str] = None
    protocol_version: Optional[str] = None
    mode: Optional[str] = None
    endpoint_url: Optional[str] = None
    auth_type: Optional[str] = None
    auth_token: Optional[str] = None
    timeout_seconds: Optional[int] = None
    retry_attempts: Optional[int] = None
    enable_audit_logging: Optional[bool] = None
    auto_sync_enabled: Optional[bool] = None
    custom_headers: Optional[dict] = None


class MCPToolAdminView(BaseModel):
    name: str
    display_name: str
    description: str
    category: str
    is_enabled: bool
    is_builtin: bool
    input_schema: dict
    custom_endpoint: Optional[str] = None
    mock_response: Optional[dict] = None
    execution_count: int = 0
    last_executed_at: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class CreateCustomMCPToolRequest(BaseModel):
    name: str
    display_name: str
    description: str
    category: Optional[str] = "custom"
    is_enabled: Optional[bool] = True
    input_schema: Optional[dict] = None
    custom_endpoint: Optional[str] = None
    mock_response: Optional[dict] = None


class UpdateMCPToolRequest(BaseModel):
    display_name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    is_enabled: Optional[bool] = None
    input_schema: Optional[dict] = None
    custom_endpoint: Optional[str] = None
    mock_response: Optional[dict] = None


class MCPTestConnectionResponse(BaseModel):
    status: str # "success" | "warning" | "error"
    message: str
    server_name: str
    mode: str
    endpoint_url: str
    latency_ms: int
    active_tools_count: int
    checked_at: str


class MCPTestRunToolRequest(BaseModel):
    tool_name: str
    arguments: dict = {}


class MCPTestRunToolResponse(BaseModel):
    tool_name: str
    status: str
    execution_mode: str
    latency_ms: int
    result: dict
    timestamp: str

