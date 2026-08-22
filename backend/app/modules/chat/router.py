from fastapi import APIRouter, Depends, HTTPException
from typing import List
from datetime import datetime
from app.core.security import get_current_user, TokenPayload, require_role
from app.core.database import db
from app.modules.chat.schemas import ChatSessionSchema, CreateSessionRequest, RenameSessionRequest

router = APIRouter(prefix="/chat", tags=["Chat History"])

@router.get("/sessions", response_model=List[ChatSessionSchema])
def list_chat_sessions(current_user: TokenPayload = Depends(require_role(["doctor", "admin"]))):
    # Filter sessions for current user or all if admin
    user_sessions = []
    for sess in db.chat_sessions.values():
        if current_user.role == "admin" or sess["user_id"] == current_user.sub:
            user_sessions.append(sess)
    return user_sessions

@router.get("/sessions/{session_id}", response_model=ChatSessionSchema)
def get_chat_session(session_id: str, current_user: TokenPayload = Depends(require_role(["doctor", "admin"]))):
    sess = db.chat_sessions.get(session_id)
    if not sess:
        raise HTTPException(status_code=404, detail="Chat session not found")
    if current_user.role != "admin" and sess["user_id"] != current_user.sub:
        raise HTTPException(status_code=403, detail="Forbidden access to chat session")
    return sess

@router.post("/sessions", response_model=ChatSessionSchema)
def create_chat_session(request: CreateSessionRequest, current_user: TokenPayload = Depends(require_role(["doctor", "admin"]))):
    session_id = f"session-{int(datetime.now().timestamp())}"
    new_sess = {
        "session_id": session_id,
        "user_id": current_user.sub,
        "title": request.title,
        "created_at": datetime.now().isoformat(),
        "patient_id": request.patient_id,
        "messages": []
    }
    db.chat_sessions[session_id] = new_sess
    return new_sess

@router.put("/sessions/{session_id}", response_model=ChatSessionSchema)
def rename_chat_session(
    session_id: str,
    request: RenameSessionRequest,
    current_user: TokenPayload = Depends(require_role(["doctor", "admin"]))
):
    sess = db.chat_sessions.get(session_id)
    if not sess:
        raise HTTPException(status_code=404, detail="Chat session not found")
    if current_user.role != "admin" and sess["user_id"] != current_user.sub:
        raise HTTPException(status_code=403, detail="Forbidden access to chat session")
    
    title = request.title.strip()
    if not title:
        raise HTTPException(status_code=400, detail="Title cannot be empty")
    
    sess["title"] = title
    return sess

@router.delete("/sessions/{session_id}")
def delete_chat_session(session_id: str, current_user: TokenPayload = Depends(require_role(["doctor", "admin"]))):
    sess = db.chat_sessions.get(session_id)
    if not sess:
        raise HTTPException(status_code=404, detail="Chat session not found")
    if current_user.role != "admin" and sess["user_id"] != current_user.sub:
        raise HTTPException(status_code=403, detail="Forbidden access to chat session")
        
    del db.chat_sessions[session_id]
    return {"status": "deleted", "session_id": session_id}

