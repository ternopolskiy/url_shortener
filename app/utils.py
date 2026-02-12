import random
import string

import httpx


ALPHABET = string.ascii_letters + string.digits
SAFE_ALPHABET = "".join(c for c in ALPHABET if c not in "0OlI1")


def generate_short_code(length: int = 6) -> str:
    """Generate random short code. 58^6 ≈ 38 billion combinations."""
    return "".join(random.choices(SAFE_ALPHABET, k=length))


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
