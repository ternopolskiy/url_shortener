import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator, HttpUrl


class URLRequest(BaseModel):
    url: str
    custom_code: Optional[str] = None

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
    original_url: str
    short_code: str
    short_url: str

    class Config:
        from_attributes = True


class URLInfo(URLResponse):
    created_at: datetime
    clicks: int
