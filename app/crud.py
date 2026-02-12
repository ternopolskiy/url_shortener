from sqlalchemy.orm import Session

from app.config import settings
from app.models import URL
from app.utils import generate_short_code


def get_url_by_code(db: Session, short_code: str) -> URL | None:
    return db.query(URL).filter(URL.short_code == short_code).first()


def get_url_by_original(db: Session, original_url: str) -> URL | None:
    return db.query(URL).filter(URL.original_url == original_url).first()


def create_short_url(
    db: Session,
    original_url: str,
    custom_code: str | None = None,
) -> URL:
    """Create short URL. Uses custom_code if provided, otherwise generates random."""
    if custom_code:
        short_code = custom_code
    else:
        for _ in range(10):
            short_code = generate_short_code(settings.SHORT_CODE_LENGTH)
            if not get_url_by_code(db, short_code):
                break
        else:
            raise RuntimeError("Failed to generate unique code")

    db_url = URL(original_url=original_url, short_code=short_code)
    db.add(db_url)
    db.commit()
    db.refresh(db_url)
    return db_url


def increment_clicks(db: Session, db_url: URL) -> None:
    db_url.clicks += 1
    db.commit()
