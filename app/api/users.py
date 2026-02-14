from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi import File, UploadFile
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


@router.get("/me/activity")
async def get_user_activity(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    days: int = Query(365, ge=1, le=365),
):
    """
    Get user activity heatmap data.
    Returns daily link creation count for the past year.
    """
    from datetime import datetime, timedelta
    from app.models import URL

    # Calculate date range
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=days - 1)

    # Get links grouped by creation date
    links_by_date = (
        db.query(
            func.date(URL.created_at).label("date"),
            func.count(URL.id).label("count"),
        )
        .filter(
            URL.user_id == current_user.id,
            func.date(URL.created_at) >= start_date,
        )
        .group_by(func.date(URL.created_at))
        .all()
    )

    # Create a dictionary for quick lookup
    activity_dict = {str(row.date): row.count for row in links_by_date}

    # Fill in all dates with 0 for missing days
    result = []
    current_date = start_date

    while current_date <= end_date:
        date_str = str(current_date)
        count = activity_dict.get(date_str, 0)

        # Determine activity level (0-4) based on count
        if count == 0:
            level = 0
        elif count == 1:
            level = 1
        elif count <= 3:
            level = 2
        elif count <= 5:
            level = 3
        else:
            level = 4

        result.append(
            {"date": date_str, "count": count, "level": level}
        )

        current_date += timedelta(days=1)

    return result


@router.post("/me/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Upload user avatar."""
    import os
    import uuid
    from pathlib import Path

    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only JPG, PNG, GIF, and WebP are allowed.",
        )

    # Validate file size (max 2MB)
    contents = await file.read()
    if len(contents) > 2 * 1024 * 1024:
        raise HTTPException(
            status_code=400, detail="File too large. Maximum size is 2MB."
        )

    # Create uploads directory if it doesn't exist
    upload_dir = Path("app/static/uploads/avatars")
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Generate unique filename
    file_extension = file.filename.split(".")[-1]
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = upload_dir / unique_filename

    # Save file
    with open(file_path, "wb") as f:
        f.write(contents)

    # Delete old avatar if exists
    if current_user.avatar_url and current_user.avatar_url.startswith(
        "/static/uploads/"
    ):
        old_file_path = Path("app" + current_user.avatar_url)
        if old_file_path.exists():
            old_file_path.unlink()

    # Update user avatar URL
    avatar_url = f"/static/uploads/avatars/{unique_filename}"
    current_user.avatar_url = avatar_url
    db.commit()

    return {"avatar_url": avatar_url, "detail": "Avatar uploaded successfully"}


@router.delete("/me/avatar")
async def delete_avatar(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete user avatar."""
    from pathlib import Path

    if not current_user.avatar_url:
        raise HTTPException(status_code=404, detail="No avatar to delete")

    # Delete file if it's a local upload
    if current_user.avatar_url.startswith("/static/uploads/"):
        file_path = Path("app" + current_user.avatar_url)
        if file_path.exists():
            file_path.unlink()

    # Clear avatar URL
    current_user.avatar_url = None
    db.commit()

    return {"detail": "Avatar deleted successfully"}


@router.patch("/me/language")
async def update_language(
    language_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update user language preference."""
    language = language_data.get("language")
    
    # Validate language
    allowed_languages = ["en", "ru", "es", "fr", "de"]
    if language not in allowed_languages:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid language. Allowed: {', '.join(allowed_languages)}",
        )

    current_user.language = language
    db.commit()

    return {"detail": "Language updated successfully", "language": language}


@router.delete("/me")
async def delete_account(
    password_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete user account and all associated data."""
    from app.core.security import verify_password
    from pathlib import Path

    password = password_data.get("password")
    
    if not password:
        raise HTTPException(
            status_code=400, detail="Password is required to delete account"
        )
    
    # Verify password
    if not verify_password(password, current_user.hashed_password):
        raise HTTPException(
            status_code=401, detail="Incorrect password"
        )
    
    # Prevent admin deletion via this endpoint
    if current_user.role == "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin accounts cannot be deleted via this endpoint. Contact support.",
        )
    
    # Delete avatar file if exists
    if current_user.avatar_url and current_user.avatar_url.startswith("/static/uploads/"):
        file_path = Path("app" + current_user.avatar_url)
        if file_path.exists():
            try:
                file_path.unlink()
            except Exception:
                pass  # Continue even if file deletion fails
    
    # Delete user (cascade will delete links and clicks)
    db.delete(current_user)
    db.commit()
    
    return {"detail": "Account deleted successfully"}
