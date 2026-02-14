import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator, HttpUrl


# ============================================
# AUTH SCHEMAS
# ============================================


class RegisterRequest(BaseModel):
    email: EmailStr
    username: str
    password: str

    @field_validator("username")
    @classmethod
    def validate_username(cls, v):
        if not re.match(r"^[a-zA-Z0-9_]{3,30}$", v):
            raise ValueError(
                "Username: 3-30 characters, letters, digits, underscore"
            )
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain uppercase letter")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain digit")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    detail: str


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    role: str
    avatar_url: Optional[str] = None
    theme_preference: str
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================
# URL SCHEMAS
# ============================================


class URLRequest(BaseModel):
    url: str
    custom_code: Optional[str] = None
    title: Optional[str] = None
    expires_at: Optional[datetime] = None
    tags: Optional[str] = None

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        if not v.startswith(("http://", "https://")):
            v = "https://" + v
        HttpUrl(v)
        return v

    @field_validator("custom_code")
    @classmethod
    def validate_custom_code(cls, v: Optional[str]) -> Optional[str]:
        """Validates custom code: 3-20 chars, alphanumeric and hyphen only."""
        if v is None:
            return v
        if not re.match(r"^[a-zA-Z0-9\-]{3,20}$", v):
            raise ValueError(
                "Custom code: 3-20 characters, letters, digits and hyphen only"
            )
        return v


class URLResponse(BaseModel):
    id: int
    original_url: str
    short_code: str
    short_url: str
    title: Optional[str] = None
    clicks_count: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class URLInfo(URLResponse):
    user_id: int
    expires_at: Optional[datetime] = None
    tags: Optional[str] = None
    updated_at: datetime


class URLUpdateRequest(BaseModel):
    title: Optional[str] = None
    is_active: Optional[bool] = None
    tags: Optional[str] = None
