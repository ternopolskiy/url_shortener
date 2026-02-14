from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.dependencies import require_admin
from app.database import get_db
from app.models import Click, URL, User

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


@router.get("/stats")
async def get_platform_stats(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Get overall platform statistics."""
    # Total users
    total_users = db.query(func.count(User.id)).scalar()
    active_users = db.query(func.count(User.id)).filter(
        User.is_active == True
    ).scalar()

    # Total links
    total_links = db.query(func.count(URL.id)).scalar()
    active_links = db.query(func.count(URL.id)).filter(
        URL.is_active == True
    ).scalar()

    # Total clicks
    total_clicks = db.query(func.sum(URL.clicks_count)).scalar() or 0

    # Recent registrations (last 7 days)
    week_ago = datetime.utcnow() - timedelta(days=7)
    new_users_week = db.query(func.count(User.id)).filter(
        User.created_at >= week_ago
    ).scalar()

    # Recent links (last 7 days)
    new_links_week = db.query(func.count(URL.id)).filter(
        URL.created_at >= week_ago
    ).scalar()

    # Clicks this week
    clicks_week = db.query(func.count(Click.id)).filter(
        Click.clicked_at >= week_ago
    ).scalar()

    # Previous week for comparison
    two_weeks_ago = datetime.utcnow() - timedelta(days=14)
    new_users_prev_week = db.query(func.count(User.id)).filter(
        User.created_at >= two_weeks_ago,
        User.created_at < week_ago
    ).scalar()

    # Calculate growth
    user_growth = 0
    if new_users_prev_week > 0:
        user_growth = round(
            ((new_users_week - new_users_prev_week) / new_users_prev_week) * 100,
            1
        )

    return {
        "total_users": total_users,
        "active_users": active_users,
        "total_links": total_links,
        "active_links": active_links,
        "total_clicks": total_clicks,
        "new_users_week": new_users_week,
        "new_links_week": new_links_week,
        "clicks_week": clicks_week,
        "user_growth": user_growth,
    }


@router.get("/users")
async def get_all_users(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = None,
):
    """Get all users with pagination and search."""
    query = db.query(User)

    if search:
        query = query.filter(
            (User.username.contains(search))
            | (User.email.contains(search))
        )

    query = query.order_by(User.created_at.desc())
    users = query.offset(skip).limit(limit).all()

    return [
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat(),
            "total_links": db.query(func.count(URL.id)).filter(
                URL.user_id == user.id
            ).scalar(),
            "total_clicks": db.query(func.sum(URL.clicks_count)).filter(
                URL.user_id == user.id
            ).scalar() or 0,
        }
        for user in users
    ]


@router.patch("/users/{user_id}")
async def update_user(
    user_id: int,
    data: dict,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Update user (role, active status)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if "role" in data:
        user.role = data["role"]

    if "is_active" in data:
        user.is_active = data["is_active"]

    db.commit()
    return {"detail": "User updated successfully"}


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Delete a user and all their data."""
    from pathlib import Path
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Prevent deletion of admin users
    if user.role == "admin":
        raise HTTPException(
            status_code=403, detail="Cannot delete admin users"
        )
    
    # Delete avatar file if exists
    if user.avatar_url and user.avatar_url.startswith("/static/uploads/"):
        file_path = Path("app" + user.avatar_url)
        if file_path.exists():
            try:
                file_path.unlink()
            except Exception:
                pass  # Continue even if file deletion fails

    # Delete user (cascade will delete all related data)
    db.delete(user)
    db.commit()
    
    return {"detail": "User deleted successfully"}


@router.get("/links")
async def get_all_links(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = None,
):
    """Get all links with pagination and search."""
    query = db.query(URL).join(User)

    if search:
        query = query.filter(
            (URL.short_code.contains(search))
            | (URL.original_url.contains(search))
            | (User.username.contains(search))
        )

    query = query.order_by(URL.created_at.desc())
    links = query.offset(skip).limit(limit).all()

    return [
        {
            "id": link.id,
            "short_code": link.short_code,
            "original_url": link.original_url,
            "clicks_count": link.clicks_count,
            "is_active": link.is_active,
            "created_at": link.created_at.isoformat(),
            "owner_username": link.owner.username,
            "owner_id": link.user_id,
        }
        for link in links
    ]


@router.delete("/links/{link_id}")
async def delete_link(
    link_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Delete a link."""
    link = db.query(URL).filter(URL.id == link_id).first()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")

    db.delete(link)
    db.commit()
    return {"detail": "Link deleted successfully"}


@router.get("/activity")
async def get_platform_activity(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
    days: int = Query(30, ge=1, le=90),
):
    """Get platform activity over time."""
    start_date = datetime.utcnow() - timedelta(days=days)

    # Users registered per day
    users_by_date = (
        db.query(
            func.date(User.created_at).label("date"),
            func.count(User.id).label("count"),
        )
        .filter(User.created_at >= start_date)
        .group_by(func.date(User.created_at))
        .all()
    )

    # Links created per day
    links_by_date = (
        db.query(
            func.date(URL.created_at).label("date"),
            func.count(URL.id).label("count"),
        )
        .filter(URL.created_at >= start_date)
        .group_by(func.date(URL.created_at))
        .all()
    )

    # Clicks per day
    clicks_by_date = (
        db.query(
            func.date(Click.clicked_at).label("date"),
            func.count(Click.id).label("count"),
        )
        .filter(Click.clicked_at >= start_date)
        .group_by(func.date(Click.clicked_at))
        .all()
    )

    # Create dictionaries for quick lookup
    users_dict = {str(row.date): row.count for row in users_by_date}
    links_dict = {str(row.date): row.count for row in links_by_date}
    clicks_dict = {str(row.date): row.count for row in clicks_by_date}

    # Fill in all dates
    result = []
    current_date = start_date.date()
    end_date = datetime.utcnow().date()

    while current_date <= end_date:
        date_str = str(current_date)
        result.append({
            "date": date_str,
            "users": users_dict.get(date_str, 0),
            "links": links_dict.get(date_str, 0),
            "clicks": clicks_dict.get(date_str, 0),
        })
        current_date += timedelta(days=1)

    return result
