from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime

from app.database import Base


class URL(Base):
    __tablename__ = "urls"

    id = Column(Integer, primary_key=True, autoincrement=True)
    original_url = Column(String, nullable=False)
    short_code = Column(String(20), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    clicks = Column(Integer, default=0)
