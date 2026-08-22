from pydantic import BaseModel, EmailStr
from typing import Optional

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str
    name: str
    role: str
    specialty: Optional[str] = None

class UserInfo(BaseModel):
    id: str
    email: str
    name: str
    role: str
    specialty: Optional[str] = None
    license_no: Optional[str] = None
    is_active: bool
