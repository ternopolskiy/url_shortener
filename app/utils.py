import random
import string

import httpx
from sqlalchemy.orm import Session

from app.config import settings

ALPHABET = string.ascii_letters + string.digits
SAFE_ALPHABET = "".join(c for c in ALPHABET if c not in "0OlI1")


def generate_short_code(
    db: Session, length: int = None, max_attempts: int = 10
) -> str:
    """
    Generate unique random short code.
    Checks database for uniqueness.
    58^6 ≈ 38 billion combinations.
    """
    from app.models import URL

    if length is None:
        length = settings.SHORT_CODE_LENGTH

    for _ in range(max_attempts):
        code = "".join(random.choices(SAFE_ALPHABET, k=length))
        existing = db.query(URL).filter(URL.short_code == code).first()
        if not existing:
            return code

    # If all attempts failed, increase length
    return generate_short_code(db, length + 1, max_attempts)


async def check_url_accessible(url: str, timeout: float = 5.0) -> bool:
    """Check if URL is accessible via HEAD request."""
    try:
        async with httpx.AsyncClient(
            follow_redirects=True, timeout=timeout
        ) as client:
            response = await client.head(url)
            return True
    except (httpx.RequestError, httpx.HTTPStatusError):
        return False
