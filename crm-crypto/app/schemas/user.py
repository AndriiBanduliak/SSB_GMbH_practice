"""
User Pydantic schemas
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from app.models.user import UserRole


# Base schema
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: UserRole = UserRole.MANAGER


# Create schema
class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


# Update schema
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


# Password change
class UserPasswordChange(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=8)


# Response schema
class User(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    is_2fa_enabled: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# 2FA schemas
class TwoFactorSetup(BaseModel):
    secret: str
    qr_code_url: str


class TwoFactorVerify(BaseModel):
    token: str


# Login schemas
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[int] = None


class Login(BaseModel):
    email: EmailStr
    password: str
    totp_token: Optional[str] = None

