from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database import get_db
from app.models import Click, URL, User

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])


@router.get("/overview")
async def get_analytics_overview(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    days: int = Query(7, ge=1, le=365),
):
    """
    Get analytics overview for current user.
    Returns comprehensive statistics about links and clicks.
    """
    # Date range
    start_date = datetime.utcnow() - timedelta(days=days)

    # Total clicks (all time)
    total_clicks = (
        db.query(func.sum(URL.clicks_count))
        .filter(URL.user_id == current_user.id)
        .scalar()
        or 0
    )

    # Total active links
    active_links = (
        db.query(func.count(URL.id))
        .filter(URL.user_id == current_user.id, URL.is_active == True)
        .scalar()
    )

    # Total links
    total_links = (
        db.query(func.count(URL.id))
        .filter(URL.user_id == current_user.id)
        .scalar()
    )

    # Average CTR (Click Through Rate)
    avg_ctr = (
        round((total_clicks / total_links) * 100, 1) if total_links > 0 else 0
    )

    # Top link
    top_link = (
        db.query(URL)
        .filter(URL.user_id == current_user.id)
        .order_by(URL.clicks_count.desc())
        .first()
    )

    # Clicks this period
    clicks_this_period = (
        db.query(func.count(Click.id))
        .join(URL)
        .filter(
            URL.user_id == current_user.id, Click.clicked_at >= start_date
        )
        .scalar()
    )

    # Previous period for comparison
    prev_start = start_date - timedelta(days=days)
    clicks_prev_period = (
        db.query(func.count(Click.id))
        .join(URL)
        .filter(
            URL.user_id == current_user.id,
            Click.clicked_at >= prev_start,
            Click.clicked_at < start_date,
        )
        .scalar()
    )

    # Calculate growth
    growth = 0
    if clicks_prev_period > 0:
        growth = round(
            ((clicks_this_period - clicks_prev_period) / clicks_prev_period)
            * 100,
            1,
        )

    return {
        "total_clicks": total_clicks,
        "active_links": active_links,
        "avg_ctr": avg_ctr,
        "top_link": {
            "short_code": top_link.short_code if top_link else None,
            "clicks": top_link.clicks_count if top_link else 0,
        },
        "clicks_this_period": clicks_this_period,
        "growth_percentage": growth,
    }


@router.get("/clicks-over-time")
async def get_clicks_over_time(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    days: int = Query(7, ge=1, le=365),
):
    """Get clicks grouped by date for chart."""
    start_date = datetime.utcnow() - timedelta(days=days)

    # Get clicks grouped by date
    clicks_by_date = (
        db.query(
            func.date(Click.clicked_at).label("date"),
            func.count(Click.id).label("count"),
        )
        .join(URL)
        .filter(
            URL.user_id == current_user.id, Click.clicked_at >= start_date
        )
        .group_by(func.date(Click.clicked_at))
        .order_by(func.date(Click.clicked_at))
        .all()
    )

    # Fill in missing dates with 0
    result = []
    current_date = start_date.date()
    end_date = datetime.utcnow().date()

    clicks_dict = {str(row.date): row.count for row in clicks_by_date}

    while current_date <= end_date:
        result.append(
            {
                "date": str(current_date),
                "clicks": clicks_dict.get(str(current_date), 0),
            }
        )
        current_date += timedelta(days=1)

    return result


@router.get("/referrers")
async def get_top_referrers(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=50),
):
    """Get top referrers."""
    referrers = (
        db.query(
            Click.referer, func.count(Click.id).label("count")
        )
        .join(URL)
        .filter(
            URL.user_id == current_user.id,
            Click.referer.isnot(None),
            Click.referer != "",
        )
        .group_by(Click.referer)
        .order_by(func.count(Click.id).desc())
        .limit(limit)
        .all()
    )

    # Count direct traffic (no referer)
    direct_count = (
        db.query(func.count(Click.id))
        .join(URL)
        .filter(
            URL.user_id == current_user.id,
            (Click.referer.is_(None)) | (Click.referer == ""),
        )
        .scalar()
    )

    result = [{"source": "Direct", "clicks": direct_count}]

    for ref in referrers:
        # Extract domain from referer
        try:
            from urllib.parse import urlparse

            domain = urlparse(ref.referer).netloc or ref.referer
            result.append({"source": domain, "clicks": ref.count})
        except:
            result.append({"source": ref.referer[:50], "clicks": ref.count})

    return result


@router.get("/devices")
async def get_device_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get device type statistics."""
    devices = (
        db.query(
            Click.device_type, func.count(Click.id).label("count")
        )
        .join(URL)
        .filter(
            URL.user_id == current_user.id, Click.device_type.isnot(None)
        )
        .group_by(Click.device_type)
        .all()
    )

    total = sum(d.count for d in devices)

    result = []
    for device in devices:
        percentage = round((device.count / total) * 100, 1) if total > 0 else 0
        result.append(
            {
                "device": device.device_type,
                "clicks": device.count,
                "percentage": percentage,
            }
        )

    # Ensure all device types are present
    device_types = {"desktop", "mobile", "tablet"}
    existing = {d["device"] for d in result}
    for dt in device_types - existing:
        result.append({"device": dt, "clicks": 0, "percentage": 0})

    return sorted(result, key=lambda x: x["clicks"], reverse=True)


@router.get("/browsers")
async def get_browser_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get browser statistics."""
    browsers = (
        db.query(Click.browser, func.count(Click.id).label("count"))
        .join(URL)
        .filter(URL.user_id == current_user.id, Click.browser.isnot(None))
        .group_by(Click.browser)
        .order_by(func.count(Click.id).desc())
        .all()
    )

    total = sum(b.count for b in browsers)

    result = []
    for browser in browsers:
        percentage = (
            round((browser.count / total) * 100, 1) if total > 0 else 0
        )
        result.append(
            {
                "browser": browser.browser,
                "clicks": browser.count,
                "percentage": percentage,
            }
        )

    return result


@router.get("/countries")
async def get_country_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=50),
):
    """Get country statistics."""
    countries = (
        db.query(Click.country, func.count(Click.id).label("count"))
        .join(URL)
        .filter(URL.user_id == current_user.id, Click.country.isnot(None))
        .group_by(Click.country)
        .order_by(func.count(Click.id).desc())
        .limit(limit)
        .all()
    )

    result = []
    for country in countries:
        result.append({"country": country.country, "clicks": country.count})

    return result


@router.get("/top-links")
async def get_top_links(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = Query(5, ge=1, le=20),
):
    """Get top performing links."""
    links = (
        db.query(URL)
        .filter(URL.user_id == current_user.id)
        .order_by(URL.clicks_count.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "id": link.id,
            "short_code": link.short_code,
            "original_url": link.original_url,
            "title": link.title,
            "clicks": link.clicks_count,
            "created_at": link.created_at.isoformat(),
        }
        for link in links
    ]
