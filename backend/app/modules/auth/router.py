from fastapi import APIRouter, HTTPException, status, Depends
from app.core.database import db
from app.core.security import verify_password, create_access_token, get_current_user, TokenPayload
from app.modules.auth.schemas import LoginRequest, TokenResponse, UserInfo

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest):
    # Search user by email
    user = None
    for u in db.users.values():
        if u["email"].lower() == request.email.lower():
            user = u
            break
            
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
        
    if not verify_password(request.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated"
        )

    access_token = create_access_token(
        subject=user["id"],
        email=user["email"],
        role=user["role"]
    )
    
    return TokenResponse(
        access_token=access_token,
        user_id=user["id"],
        email=user["email"],
        name=user["name"],
        role=user["role"],
        specialty=user.get("specialty")
    )

@router.get("/me", response_model=UserInfo)
def get_me(current_user: TokenPayload = Depends(get_current_user)):
    user = db.users.get(current_user.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserInfo(
        id=user["id"],
        email=user["email"],
        name=user["name"],
        role=user["role"],
        specialty=user.get("specialty"),
        license_no=user.get("license_no"),
        is_active=user.get("is_active", True)
    )
