from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from datetime import datetime, timedelta
from collections import Counter
from app.core.security import require_role, get_password_hash, TokenPayload
from app.core.database import db
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
)
from app.modules.rag.rag_service import qdrant_rag_service

router = APIRouter(prefix="/admin", tags=["Admin Dashboard"])

@router.get("/stats", response_model=AdminStatsResponse)
def get_admin_stats(current_user: TokenPayload = Depends(require_role(["admin"]))):
    doctors_count = sum(1 for u in db.users.values() if u.get("role") == "doctor")
    admins_count = sum(1 for u in db.users.values() if u.get("role") == "admin")
    total_tokens = sum(log.get("tokens_used", 0) for log in db.audit_logs)
    
    return AdminStatsResponse(
        total_doctors=doctors_count,
        total_admins=admins_count,
        total_chat_sessions=len(db.chat_sessions),
        total_queries_run=len(db.audit_logs),
        total_gemini_tokens=total_tokens,
        gemini_model_active=settings.GEMINI_MODEL_NAME
    )


@router.get("/analytics", response_model=UsageAnalyticsResponse)
def get_usage_analytics(current_user: TokenPayload = Depends(require_role(["admin"]))):
    """Aggregated usage data for the admin dashboard without exposing patient content."""
    logs = db.audit_logs
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
    return [UserAdminView(**u) for u in db.users.values()]

@router.post("/users", response_model=UserAdminView)
def create_user(request: CreateUserRequest, current_user: TokenPayload = Depends(require_role(["admin"]))):
    # Check if email exists
    for u in db.users.values():
        if u["email"].lower() == request.email.lower():
            raise HTTPException(status_code=400, detail="User with this email already exists")

    new_id = f"u{len(db.users) + 1}"
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
    db.users[new_id] = new_user
    return UserAdminView(**new_user)

@router.post("/users/{user_id}/toggle-status")
def toggle_user_status(user_id: str, current_user: TokenPayload = Depends(require_role(["admin"]))):
    user = db.users.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user["is_active"] = not user.get("is_active", True)
    return {"status": "success", "user_id": user_id, "is_active": user["is_active"]}

@router.get("/audit-logs", response_model=List[AuditLogItem])
def get_audit_logs(current_user: TokenPayload = Depends(require_role(["admin"]))):
    return [AuditLogItem(**log) for log in db.audit_logs]
