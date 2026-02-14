from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Click, URL

router = APIRouter()


@router.get("/{short_code}")
async def redirect_to_url(
    short_code: str, request: Request, db: Session = Depends(get_db)
):
    """
    Redirect to original URL by short code.
    HTTP 302 temporary redirect.
    Track click analytics.
    """
    url = db.query(URL).filter(URL.short_code == short_code).first()
    if not url:
        raise HTTPException(status_code=404, detail="Link not found")

    # Check if active and not expired
    if not url.is_active:
        raise HTTPException(status_code=410, detail="Link is disabled")

    if url.is_expired:
        raise HTTPException(status_code=410, detail="Link has expired")

    # Track click
    _track_click(db, url, request)

    # Increment counter
    url.clicks_count += 1
    db.commit()

    return RedirectResponse(url=url.original_url, status_code=302)


def _track_click(db: Session, url: URL, request: Request):
    """Track click analytics."""
    # Extract data from request
    user_agent = request.headers.get("user-agent", "")
    referer = request.headers.get("referer")
    
    # Get client IP (handle proxy headers)
    ip = request.client.host if request.client else None
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        ip = forwarded.split(",")[0].strip()

    # Parse user agent (simplified - можно использовать user-agents library)
    device_type = _detect_device(user_agent)
    browser = _detect_browser(user_agent)
    os = _detect_os(user_agent)

    # Create click record
    click = Click(
        url_id=url.id,
        ip_address=ip,
        user_agent=user_agent[:500] if user_agent else None,
        referer=referer[:500] if referer else None,
        device_type=device_type,
        browser=browser,
        os=os,
        # country and city would require GeoIP database
    )
    db.add(click)


def _detect_device(user_agent: str) -> str:
    """Detect device type from user agent."""
    ua_lower = user_agent.lower()
    if any(x in ua_lower for x in ["mobile", "android", "iphone"]):
        return "mobile"
    elif "tablet" in ua_lower or "ipad" in ua_lower:
        return "tablet"
    return "desktop"


def _detect_browser(user_agent: str) -> str:
    """Detect browser from user agent."""
    ua_lower = user_agent.lower()
    if "edg" in ua_lower:
        return "Edge"
    elif "chrome" in ua_lower:
        return "Chrome"
    elif "safari" in ua_lower:
        return "Safari"
    elif "firefox" in ua_lower:
        return "Firefox"
    return "Other"


def _detect_os(user_agent: str) -> str:
    """Detect OS from user agent."""
    ua_lower = user_agent.lower()
    if "windows" in ua_lower:
        return "Windows"
    elif "mac" in ua_lower:
        return "macOS"
    elif "linux" in ua_lower:
        return "Linux"
    elif "android" in ua_lower:
        return "Android"
    elif "ios" in ua_lower or "iphone" in ua_lower:
        return "iOS"
    return "Other"
