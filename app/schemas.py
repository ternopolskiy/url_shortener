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
        """Validate password strength with a unified error message."""
        has_min_length = len(v) >= 8
        has_uppercase = bool(re.search(r"[A-Z]", v))
        has_digit = bool(re.search(r"[0-9]", v))

        if not has_min_length or not has_uppercase or not has_digit:
            missing = []
            if not has_min_length:
                missing.append("at least 8 characters")
            if not has_uppercase:
                missing.append("an uppercase letter")
            if not has_digit:
                missing.append("a number")
            raise ValueError(
                f"Make your password more secure: use {', '.join(missing)}. "
                "Use numbers, letters, and capital letters."
            )
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


# ============================================
# QR CODE SCHEMAS
# ============================================

class QRCodeCreateRequest(BaseModel):
    """Запрос на создание QR-кода."""
    content: str  # URL или текст для кодирования
    title: Optional[str] = None
    url_id: Optional[int] = None  # привязка к существующей ссылке

    # Стилизация
    foreground_color: str = "#000000"
    background_color: str = "#FFFFFF"
    style: str = "square"  # square | rounded | dots | circle
    box_size: int = 10
    border_size: int = 4
    error_correction: str = "M"  # L | M | Q | H

    # Логотип (base64 строка, опционально)
    logo_base64: Optional[str] = None

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Содержимое QR-кода не может быть пустым")
        if len(v) > 2000:
            raise ValueError("Максимальная длина — 2000 символов")
        return v

    @field_validator("foreground_color", "background_color")
    @classmethod
    def validate_color(cls, v: str) -> str:
        if not re.match(r"^#[0-9A-Fa-f]{6}$", v):
            raise ValueError("Цвет должен быть в формате #RRGGBB")
        return v.upper()

    @field_validator("style")
    @classmethod
    def validate_style(cls, v: str) -> str:
        allowed = ["square", "rounded", "dots", "circle"]
        if v not in allowed:
            raise ValueError(f"Стиль должен быть одним из: {', '.join(allowed)}")
        return v

    @field_validator("box_size")
    @classmethod
    def validate_box_size(cls, v: int) -> int:
        if not (5 <= v <= 20):
            raise ValueError("Размер модуля: от 5 до 20")
        return v

    @field_validator("border_size")
    @classmethod
    def validate_border_size(cls, v: int) -> int:
        if not (0 <= v <= 10):
            raise ValueError("Размер границы: от 0 до 10")
        return v

    @field_validator("error_correction")
    @classmethod
    def validate_error_correction(cls, v: str) -> str:
        if v not in ("L", "M", "Q", "H"):
            raise ValueError("Error correction: L, M, Q или H")
        return v


class QRCodePreviewRequest(BaseModel):
    """Запрос на превью (без сохранения в БД)."""
    content: str = "https://example.com"
    foreground_color: str = "#000000"
    background_color: str = "#FFFFFF"
    style: str = "square"
    box_size: int = 10
    border_size: int = 4
    error_correction: str = "M"
    logo_base64: Optional[str] = None


class QRCodeResponse(BaseModel):
    """Ответ с данными QR-кода."""
    id: int
    content: str
    title: Optional[str]
    url_id: Optional[int]
    qr_image_base64: str
    foreground_color: str
    background_color: str
    style: str
    box_size: int
    border_size: int
    error_correction: str
    logo_base64: Optional[str]
    downloads_count: int
    created_at: str
    updated_at: str

    # Дополнительные поля (если привязана ссылка)
    linked_short_code: Optional[str] = None
    linked_clicks: Optional[int] = None

    class Config:
        from_attributes = True


class QRCodeListResponse(BaseModel):
    """Список QR-кодов с пагинацией."""
    items: list[QRCodeResponse]
    total: int
    page: int
    per_page: int
    pages: int


class QRCodeUpdateRequest(BaseModel):
    """Обновление QR-кода (только title)."""
    title: Optional[str] = None


class QRCodePreviewResponse(BaseModel):
    """Ответ с превью (только изображение)."""
    qr_image_base64: str
