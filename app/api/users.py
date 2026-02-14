from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database import get_db
from app.models import URL, User

router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.get("/me/stats")
async def get_my_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get current user statistics."""
    # Total links
    total_links = (
        db.query(func.count(URL.id))
        .filter(URL.user_id == current_user.id)
        .scalar()
    )

    # Total clicks
    total_clicks = (
        db.query(func.sum(URL.clicks_count))
        .filter(URL.user_id == current_user.id)
        .scalar()
        or 0
    )

    # Click rate (percentage of links that have been clicked)
    links_with_clicks = (
        db.query(func.count(URL.id))
        .filter(URL.user_id == current_user.id, URL.clicks_count > 0)
        .scalar()
    )

    click_rate = (
        round((links_with_clicks / total_links) * 100, 1)
        if total_links > 0
        else 0
    )

    # Recent links (last 5)
    recent_links = (
        db.query(URL)
        .filter(URL.user_id == current_user.id)
        .order_by(URL.created_at.desc())
        .limit(5)
        .all()
    )

    return {
        "total_links": total_links,
        "total_clicks": total_clicks,
        "click_rate": click_rate,
        "recent_links": [
            {
                "id": link.id,
                "short_code": link.short_code,
                "short_url": f"{link.short_code}",
                "original_url": link.original_url,
                "clicks_count": link.clicks_count,
                "created_at": link.created_at.isoformat(),
            }
            for link in recent_links
        ],
    }


@router.patch("/me/theme")
async def update_theme(
    theme_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update user theme preference."""
    theme = theme_data.get("theme")
    if theme not in ["light", "dark"]:
        return {"detail": "Invalid theme"}

    current_user.theme_preference = theme
    db.commit()

    return {"detail": "Theme updated"}


@router.patch("/me")
async def update_profile(
    profile_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update user profile (username, email)."""
    username = profile_data.get("username")
    email = profile_data.get("email")

    # Check username uniqueness
    if username and username != current_user.username:
        existing = (
            db.query(User).filter(User.username == username).first()
        )
        if existing:
            raise HTTPException(
                status_code=409, detail="Username already taken"
            )
        current_user.username = username

    # Check email uniqueness
    if email and email != current_user.email:
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            raise HTTPException(
                status_code=409, detail="Email already registered"
            )
        current_user.email = email

    db.commit()
    return {"detail": "Profile updated successfully"}


@router.patch("/me/password")
async def change_password(
    password_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Change user password."""
    from app.core.security import hash_password, verify_password

    current_password = password_data.get("current_password")
    new_password = password_data.get("new_password")

    if not current_password or not new_password:
        raise HTTPException(
            status_code=400, detail="Both passwords required"
        )

    # Verify current password
    if not verify_password(current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=401, detail="Current password is incorrect"
        )

    # Validate new password
    if len(new_password) < 8:
        raise HTTPException(
            status_code=400, detail="Password must be at least 8 characters"
        )

    # Update password
    current_user.hashed_password = hash_password(new_password)
    db.commit()

    return {"detail": "Password changed successfully"}
