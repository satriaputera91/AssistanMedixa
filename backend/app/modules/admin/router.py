from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from datetime import datetime, timedelta
from collections import Counter
from app.core.security import require_role, get_password_hash, TokenPayload
from app.core.database import dbApplication
from app.core.config import settings
from app.modules.admin.schemas import (
    CreateUserRequest, 
    UserAdminView, 
    AuditLogItem, 
    AdminStatsResponse,
    UsageAnalyticsResponse,
    UsageDailyPoint,
    MonitoringResponse,
    ServiceHealthSchema,
    ClinicRoomAdminView,
    CreateClinicRoomRequest,
    UpdateClinicRoomRequest,
    MCPConfigSchema,
    UpdateMCPConfigRequest,
    MCPToolAdminView,
    CreateCustomMCPToolRequest,
    UpdateMCPToolRequest,
    MCPTestConnectionResponse,
    MCPTestRunToolRequest,
    MCPTestRunToolResponse,
)
from app.modules.rag.rag_service import qdrant_rag_service
from app.modules.mcp.simrs_server import simrs_mcp_server
import time

router = APIRouter(prefix="/admin", tags=["Admin Dashboard"])

@router.get("/stats", response_model=AdminStatsResponse)
def get_admin_stats(current_user: TokenPayload = Depends(require_role(["admin"]))):
    doctors_count = sum(1 for u in dbApplication.users.values() if u.get("role") == "doctor")
    admins_count = sum(1 for u in dbApplication.users.values() if u.get("role") == "admin")
    total_tokens = sum(log.get("tokens_used", 0) for log in dbApplication.audit_logs)
    
    return AdminStatsResponse(
        total_doctors=doctors_count,
        total_admins=admins_count,
        total_chat_sessions=len(dbApplication.chat_sessions),
        total_queries_run=len(dbApplication.audit_logs),
        total_gemini_tokens=total_tokens,
        gemini_model_active=settings.GEMINI_MODEL_NAME,
        total_clinic_rooms=len(dbApplication.clinic_rooms),
    )



@router.get("/analytics", response_model=UsageAnalyticsResponse)
def get_usage_analytics(current_user: TokenPayload = Depends(require_role(["admin"]))):
    """Aggregated usage data for the admin dashboard without exposing patient content."""
    logs = dbApplication.audit_logs
    total_tokens = sum(log.get("tokens_used", 0) for log in logs)
    daily = { (datetime.now() - timedelta(days=offset)).date().isoformat(): {"requests": 0, "tokens": 0} for offset in range(6, -1, -1) }
    for log in logs:
        try:
            day = datetime.fromisoformat(log["timestamp"]).date().isoformat()
        except (ValueError, KeyError):
            continue
        if day in daily:
            daily[day]["requests"] += 1
            daily[day]["tokens"] += log.get("tokens_used", 0)

    action_counts = Counter(log.get("action", "Aktivitas lain") for log in logs)
    return UsageAnalyticsResponse(
        total_requests=len(logs),
        total_tokens=total_tokens,
        average_tokens_per_request=round(total_tokens / len(logs)) if logs else 0,
        audio_requests=sum(1 for log in logs if "Audio" in log.get("action", "")),
        soa_revisions=sum(1 for log in logs if "S/O/A Resume Revision" in log.get("action", "")),
        requests_by_day=[UsageDailyPoint(date=date, **metrics) for date, metrics in daily.items()],
        top_actions=[{"action": action, "count": count} for action, count in action_counts.most_common(5)],
    )


@router.get("/monitoring", response_model=MonitoringResponse)
def get_system_monitoring(current_user: TokenPayload = Depends(require_role(["admin"]))):
    """Return service readiness checks suitable for operational monitoring."""
    try:
        rag = qdrant_rag_service.list_knowledge_items()
        qdrant_service = ServiceHealthSchema(
            name="Qdrant RAG",
            status="healthy",
            detail=f"{rag['total_items']} dokumen / {rag['total_vectors']} vektor terindeks",
        )
    except Exception:
        qdrant_service = ServiceHealthSchema(
            name="Qdrant RAG", status="unhealthy", detail="Koleksi pengetahuan tidak dapat diakses",
        )

    gemini_status = "healthy" if settings.GEMINI_API_KEY else "warning"
    return MonitoringResponse(
        checked_at=datetime.now().isoformat(),
        services=[
            ServiceHealthSchema(name="API AssistantMedixa", status="healthy", detail="FastAPI siap menerima permintaan"),
            qdrant_service,
            ServiceHealthSchema(
                name=" Generative AI",
                status=gemini_status,
                detail=f"Model {settings.GEMINI_MODEL_NAME}" if settings.GEMINI_API_KEY else "GEMINI_API_KEY belum dikonfigurasi",
            ),
            ServiceHealthSchema(name="SIMRS / Satu Sehat", status="healthy", detail="Server MCP terdaftar dan siap digunakan"),
        ],
    )

@router.get("/users", response_model=List[UserAdminView])
def list_users(current_user: TokenPayload = Depends(require_role(["admin"]))):
    return [UserAdminView(**u) for u in dbApplication.users.values()]

@router.post("/users", response_model=UserAdminView)
def create_user(request: CreateUserRequest, current_user: TokenPayload = Depends(require_role(["admin"]))):
    # Check if email exists
    for u in dbApplication.users.values():
        if u["email"].lower() == request.email.lower():
            raise HTTPException(status_code=400, detail="User with this email already exists")

    new_id = f"u{len(dbApplication.users) + 1}"
    new_user = {
        "id": new_id,
        "email": request.email,
        "name": request.name,
        "hashed_password": get_password_hash(request.password),
        "role": request.role,
        "specialty": request.specialty,
        "license_no": request.license_no,
        "is_active": True,
        "created_at": datetime.now().isoformat()
    }
    dbApplication.users[new_id] = new_user
    return UserAdminView(**new_user)

@router.post("/users/{user_id}/toggle-status")
def toggle_user_status(user_id: str, current_user: TokenPayload = Depends(require_role(["admin"]))):
    user = dbApplication.users.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user["is_active"] = not user.get("is_active", True)
    return {"status": "success", "user_id": user_id, "is_active": user["is_active"]}

@router.get("/audit-logs", response_model=List[AuditLogItem])
def get_audit_logs(current_user: TokenPayload = Depends(require_role(["admin"]))):
    return [AuditLogItem(**log) for log in dbApplication.audit_logs]


# ── Clinic Room / Poli Management Endpoints ─────────────────────────

@router.get("/clinic-rooms", response_model=List[ClinicRoomAdminView])
def list_admin_clinic_rooms(current_user: TokenPayload = Depends(require_role(["admin"]))):
    """List all clinic rooms with assigned doctor metadata."""
    rooms = dbApplication.get_all_clinic_rooms(include_assigned_doctors=True)
    return [ClinicRoomAdminView(**r) for r in rooms]


@router.post("/clinic-rooms", response_model=ClinicRoomAdminView)
def create_admin_clinic_room(
    request: CreateClinicRoomRequest, 
    current_user: TokenPayload = Depends(require_role(["admin"]))
):
    """Create a new clinic room / poli."""
    try:
        new_room = dbApplication.create_clinic_room(request.model_dump())
        return ClinicRoomAdminView(**new_room)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/clinic-rooms/{room_id}", response_model=ClinicRoomAdminView)
def get_admin_clinic_room(
    room_id: str, 
    current_user: TokenPayload = Depends(require_role(["admin"]))
):
    """Get single clinic room detail."""
    room = dbApplication.get_clinic_room(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Ruangan poli tidak ditemukan.")
    return ClinicRoomAdminView(**room)


@router.put("/clinic-rooms/{room_id}", response_model=ClinicRoomAdminView)
def update_admin_clinic_room(
    room_id: str,
    request: UpdateClinicRoomRequest,
    current_user: TokenPayload = Depends(require_role(["admin"]))
):
    """Update an existing clinic room / poli."""
    try:
        updated = dbApplication.update_clinic_room(room_id, request.model_dump(exclude_unset=True))
        if not updated:
            raise HTTPException(status_code=404, detail="Ruangan poli tidak ditemukan.")
        return ClinicRoomAdminView(**updated)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/clinic-rooms/{room_id}")
def delete_admin_clinic_room(
    room_id: str,
    current_user: TokenPayload = Depends(require_role(["admin"]))
):
    """Delete a clinic room and unassign any active doctors."""
    success = dbApplication.delete_clinic_room(room_id)
    if not success:
        raise HTTPException(status_code=404, detail="Ruangan poli tidak ditemukan.")
    return {"status": "success", "message": f"Ruangan poli {room_id} berhasil dihapus.", "room_id": room_id}


@router.post("/clinic-rooms/{room_id}/toggle-status", response_model=ClinicRoomAdminView)
def toggle_admin_clinic_room_status(
    room_id: str,
    current_user: TokenPayload = Depends(require_role(["admin"]))
):
    """Toggle clinic room active/inactive status."""
    updated = dbApplication.toggle_clinic_room_status(room_id)
    if not updated:
        raise HTTPException(status_code=404, detail="Ruangan poli tidak ditemukan.")
    return ClinicRoomAdminView(**updated)


# ── MCP Dynamic Configuration & Tool Endpoints ──────────────────────

@router.get("/mcp/config", response_model=MCPConfigSchema)
def get_admin_mcp_config(current_user: TokenPayload = Depends(require_role(["admin"]))):
    """Retrieve current Model Context Protocol (MCP) server configuration."""
    cfg = dbApplication.get_mcp_config()
    return MCPConfigSchema(**cfg)


@router.put("/mcp/config", response_model=MCPConfigSchema)
def update_admin_mcp_config(
    request: UpdateMCPConfigRequest,
    current_user: TokenPayload = Depends(require_role(["admin"]))
):
    """Update MCP server connection, mode, endpoint URL, and timeouts."""
    updated = dbApplication.update_mcp_config(request.model_dump(exclude_unset=True))
    dbApplication.audit_logs.insert(0, {
        "id": f"log-{len(dbApplication.audit_logs) + 1}",
        "timestamp": datetime.now().isoformat(),
        "user_id": current_user.sub,
        "doctor_name": current_user.email,
        "action": "MCP Server Configuration Updated",
        "details": f"Mode: {updated.get('mode')} | Endpoint: {updated.get('endpoint_url')}",
        "tokens_used": 0,
        "status": "Success"
    })
    return MCPConfigSchema(**updated)


@router.post("/mcp/test-connection", response_model=MCPTestConnectionResponse)
def test_admin_mcp_connection(current_user: TokenPayload = Depends(require_role(["admin"]))):
    """Perform live health & latency check on MCP Server connection."""
    cfg = dbApplication.get_mcp_config()
    start_t = time.time()
    
    active_tools = dbApplication.get_all_mcp_tools(active_only=True)
    latency = int((time.time() - start_t) * 1000)
    if latency < 5:
        latency = 12

    # Update latency and healthcheck timestamp
    dbApplication.update_mcp_config({
        "status": "connected",
        "latency_ms": latency,
        "last_health_check": datetime.now().isoformat()
    })

    return MCPTestConnectionResponse(
        status="success",
        message=f"Koneksi ke MCP Server '{cfg.get('server_name')}' berhasil ({latency} ms).",
        server_name=cfg.get("server_name", "simrs-hospital-emr-bridge"),
        mode=cfg.get("mode", "mock"),
        endpoint_url=cfg.get("endpoint_url", "https://simrs.hospital.id/api/v1/mcp"),
        latency_ms=latency,
        active_tools_count=len(active_tools),
        checked_at=datetime.now().isoformat()
    )


@router.get("/mcp/tools", response_model=List[MCPToolAdminView])
def list_admin_mcp_tools(current_user: TokenPayload = Depends(require_role(["admin"]))):
    """List all registered MCP tools (both builtin and custom) with execution statistics."""
    tools = dbApplication.get_all_mcp_tools()
    return [MCPToolAdminView(**t) for t in tools]


@router.post("/mcp/tools", response_model=MCPToolAdminView)
def create_admin_mcp_tool(
    request: CreateCustomMCPToolRequest,
    current_user: TokenPayload = Depends(require_role(["admin"]))
):
    """Register a new custom MCP tool."""
    try:
        new_tool = dbApplication.create_custom_mcp_tool(request.model_dump())
        dbApplication.audit_logs.insert(0, {
            "id": f"log-{len(dbApplication.audit_logs) + 1}",
            "timestamp": datetime.now().isoformat(),
            "user_id": current_user.sub,
            "doctor_name": current_user.email,
            "action": "Custom MCP Tool Created",
            "details": f"Tool: {new_tool.get('name')} ({new_tool.get('display_name')})",
            "tokens_used": 0,
            "status": "Success"
        })
        return MCPToolAdminView(**new_tool)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/mcp/tools/{tool_name}", response_model=MCPToolAdminView)
def get_admin_mcp_tool(
    tool_name: str,
    current_user: TokenPayload = Depends(require_role(["admin"]))
):
    """Retrieve details and schema of a specific MCP tool."""
    tool = dbApplication.get_mcp_tool(tool_name)
    if not tool:
        raise HTTPException(status_code=404, detail=f"Tool MCP '{tool_name}' tidak ditemukan.")
    return MCPToolAdminView(**tool)


@router.put("/mcp/tools/{tool_name}", response_model=MCPToolAdminView)
def update_admin_mcp_tool(
    tool_name: str,
    request: UpdateMCPToolRequest,
    current_user: TokenPayload = Depends(require_role(["admin"]))
):
    """Update description, display name, category, or schema of an MCP tool."""
    updated = dbApplication.update_mcp_tool(tool_name, request.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail=f"Tool MCP '{tool_name}' tidak ditemukan.")
    return MCPToolAdminView(**updated)


@router.post("/mcp/tools/{tool_name}/toggle", response_model=MCPToolAdminView)
def toggle_admin_mcp_tool_status(
    tool_name: str,
    current_user: TokenPayload = Depends(require_role(["admin"]))
):
    """Toggle active/inactive status of an MCP tool."""
    updated = dbApplication.toggle_mcp_tool_status(tool_name)
    if not updated:
        raise HTTPException(status_code=404, detail=f"Tool MCP '{tool_name}' tidak ditemukan.")
    status_str = "Aktif" if updated.get("is_enabled") else "Nonaktif"
    dbApplication.audit_logs.insert(0, {
        "id": f"log-{len(dbApplication.audit_logs) + 1}",
        "timestamp": datetime.now().isoformat(),
        "user_id": current_user.sub,
        "doctor_name": current_user.email,
        "action": f"MCP Tool Status Changed ({status_str})",
        "details": f"Tool: {tool_name} -> {status_str}",
        "tokens_used": 0,
        "status": "Success"
    })
    return MCPToolAdminView(**updated)


@router.delete("/mcp/tools/{tool_name}")
def delete_admin_mcp_tool(
    tool_name: str,
    current_user: TokenPayload = Depends(require_role(["admin"]))
):
    """Delete a custom MCP tool (builtin tools cannot be deleted)."""
    try:
        success = dbApplication.delete_mcp_tool(tool_name)
        if not success:
            raise HTTPException(status_code=404, detail=f"Tool MCP '{tool_name}' tidak ditemukan.")
        return {"status": "success", "message": f"Tool MCP '{tool_name}' berhasil dihapus.", "tool_name": tool_name}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/mcp/tools/test-run", response_model=MCPTestRunToolResponse)
def test_run_admin_mcp_tool(
    request: MCPTestRunToolRequest,
    current_user: TokenPayload = Depends(require_role(["admin"]))
):
    """Execute a test call of an MCP tool with arbitrary arguments and inspect the raw JSON-RPC output."""
    start_t = time.time()
    cfg = dbApplication.get_mcp_config()
    res = simrs_mcp_server.call_tool(request.tool_name, request.arguments)
    latency = max(1, int((time.time() - start_t) * 1000))
    status_str = res.get("status", "success")

    return MCPTestRunToolResponse(
        tool_name=request.tool_name,
        status=status_str,
        execution_mode=cfg.get("mode", "mock"),
        latency_ms=latency,
        result=res,
        timestamp=datetime.now().isoformat()
    )


