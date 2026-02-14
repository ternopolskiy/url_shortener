from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.config import settings
from app.core.dependencies import get_current_user
from app.database import get_db
from app.models import URL, User
from app.schemas import URLInfo, URLRequest, URLResponse, URLUpdateRequest
from app.utils import check_url_accessible, generate_short_code

router = APIRouter(prefix="/api/v1/links", tags=["links"])


@router.post("", response_model=URLResponse, status_code=201)
async def create_link(
    data: URLRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a short link."""
    # Check URL accessibility
    is_accessible = await check_url_accessible(data.url)
    if not is_accessible:
        raise HTTPException(
            status_code=400,
            detail="URL is not accessible. Check the link.",
        )

    # Check custom code uniqueness
    if data.custom_code:
        existing = (
            db.query(URL).filter(URL.short_code == data.custom_code).first()
        )
        if existing:
            raise HTTPException(
                status_code=409,
                detail=f"Code '{data.custom_code}' is already taken.",
            )
        short_code = data.custom_code
    else:
        # Check if user already has this URL
        existing = (
            db.query(URL)
            .filter(
                URL.user_id == current_user.id,
                URL.original_url == data.url,
            )
            .first()
        )
        if existing:
            return _url_to_response(existing)

        # Generate unique short code
        short_code = generate_short_code(db)

    # Create URL
    url = URL(
        user_id=current_user.id,
        original_url=data.url,
        short_code=short_code,
        title=data.title,
        expires_at=data.expires_at,
        tags=data.tags,
    )
    db.add(url)
    db.commit()
    db.refresh(url)

    return _url_to_response(url)


@router.get("", response_model=List[URLResponse])
async def get_my_links(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = None,
    active_only: bool = False,
):
    """Get user's links with pagination and search."""
    query = db.query(URL).filter(URL.user_id == current_user.id)

    if search:
        query = query.filter(
            (URL.short_code.contains(search))
            | (URL.original_url.contains(search))
            | (URL.title.contains(search))
        )

    if active_only:
        query = query.filter(URL.is_active == True)

    query = query.order_by(URL.created_at.desc())
    urls = query.offset(skip).limit(limit).all()

    return [_url_to_response(url) for url in urls]


@router.get("/{link_id}", response_model=URLInfo)
async def get_link(
    link_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get link details."""
    url = (
        db.query(URL)
        .filter(URL.id == link_id, URL.user_id == current_user.id)
        .first()
    )
    if not url:
        raise HTTPException(status_code=404, detail="Link not found")

    return URLInfo(
        id=url.id,
        user_id=url.user_id,
        original_url=url.original_url,
        short_code=url.short_code,
        short_url=f"{settings.BASE_URL}/{url.short_code}",
        title=url.title,
        clicks_count=url.clicks_count,
        is_active=url.is_active,
        expires_at=url.expires_at,
        tags=url.tags,
        created_at=url.created_at,
        updated_at=url.updated_at,
    )


@router.patch("/{link_id}", response_model=URLResponse)
async def update_link(
    link_id: int,
    data: URLUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update link (title, active status, tags)."""
    url = (
        db.query(URL)
        .filter(URL.id == link_id, URL.user_id == current_user.id)
        .first()
    )
    if not url:
        raise HTTPException(status_code=404, detail="Link not found")

    if data.title is not None:
        url.title = data.title
    if data.is_active is not None:
        url.is_active = data.is_active
    if data.tags is not None:
        url.tags = data.tags

    db.commit()
    db.refresh(url)

    return _url_to_response(url)


@router.delete("/{link_id}")
async def delete_link(
    link_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a link."""
    url = (
        db.query(URL)
        .filter(URL.id == link_id, URL.user_id == current_user.id)
        .first()
    )
    if not url:
        raise HTTPException(status_code=404, detail="Link not found")

    db.delete(url)
    db.commit()

    return {"detail": "Link deleted successfully"}


def _url_to_response(url: URL) -> URLResponse:
    """Convert URL model to response schema."""
    return URLResponse(
        id=url.id,
        original_url=url.original_url,
        short_code=url.short_code,
        short_url=f"{settings.BASE_URL}/{url.short_code}",
        title=url.title,
        clicks_count=url.clicks_count,
        is_active=url.is_active,
        created_at=url.created_at,
    )
