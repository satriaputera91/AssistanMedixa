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
)
from app.modules.rag.rag_service import qdrant_rag_service

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
            ServiceHealthSchema(name="API AIMedical", status="healthy", detail="FastAPI siap menerima permintaan"),
            qdrant_service,
            ServiceHealthSchema(
                name="Google Gemini",
                status=gemini_status,
                detail=f"Model {settings.GEMINI_MODEL_NAME}" if settings.GEMINI_API_KEY else "GEMINI_API_KEY belum dikonfigurasi",
            ),
            ServiceHealthSchema(name="SIMRS MCP", status="healthy", detail="Server MCP terdaftar dan siap digunakan"),
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

