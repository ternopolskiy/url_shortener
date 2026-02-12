from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.config import settings
from app.crud import (
    create_short_url,
    get_url_by_code,
    get_url_by_original,
    increment_clicks,
)
from app.database import get_db
from app.schemas import URLRequest, URLResponse, URLInfo
from app.utils import check_url_accessible


router = APIRouter()


@router.post("/api/shorten", response_model=URLResponse, status_code=201)
async def shorten_url(request: URLRequest, db: Session = Depends(get_db)):
    """Create short URL."""
    is_accessible = await check_url_accessible(request.url)
    if not is_accessible:
        raise HTTPException(
            status_code=400,
            detail="URL is not accessible. Check the link.",
        )

    if request.custom_code:
        existing = get_url_by_code(db, request.custom_code)
        if existing:
            raise HTTPException(
                status_code=409,
                detail=f"Code '{request.custom_code}' is already taken.",
            )

    if not request.custom_code:
        existing = get_url_by_original(db, request.url)
        if existing:
            return URLResponse(
                original_url=existing.original_url,
                short_code=existing.short_code,
                short_url=f"{settings.BASE_URL}/{existing.short_code}",
            )

    db_url = create_short_url(db, request.url, request.custom_code)

    return URLResponse(
        original_url=db_url.original_url,
        short_code=db_url.short_code,
        short_url=f"{settings.BASE_URL}/{db_url.short_code}",
    )


@router.get("/{short_code}")
async def redirect_to_url(short_code: str, db: Session = Depends(get_db)):
    """Redirect to original URL by short code. HTTP 302 temporary redirect."""
    db_url = get_url_by_code(db, short_code)
    if not db_url:
        raise HTTPException(status_code=404, detail="Link not found")

    increment_clicks(db, db_url)
    return RedirectResponse(url=db_url.original_url, status_code=302)


@router.get("/api/info/{short_code}", response_model=URLInfo)
async def get_url_info(short_code: str, db: Session = Depends(get_db)):
    """Get URL info: original URL, creation date, clicks."""
    db_url = get_url_by_code(db, short_code)
    if not db_url:
        raise HTTPException(status_code=404, detail="Link not found")

    return URLInfo(
        original_url=db_url.original_url,
        short_code=db_url.short_code,
        short_url=f"{settings.BASE_URL}/{db_url.short_code}",
        created_at=db_url.created_at,
        clicks=db_url.clicks,
    )
