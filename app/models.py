import enum
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.database import Base


class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), default=UserRole.USER, nullable=False)
    avatar_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    theme_preference = Column(String(10), default="light")

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    # Relationships
    urls = relationship(
        "URL", back_populates="owner", cascade="all, delete-orphan"
    )
    qr_codes = relationship("QRCode", back_populates="owner")
    bio_pages = relationship("BioPage", back_populates="owner")

    @property
    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN

    @property
    def total_links(self) -> int:
        return len(self.urls)

    @property
    def total_clicks(self) -> int:
        return sum(url.clicks_count for url in self.urls)


class URL(Base):
    __tablename__ = "urls"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    original_url = Column(Text, nullable=False)
    short_code = Column(String(20), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime, nullable=True)
    clicks_count = Column(Integer, default=0)
    tags = Column(String(500), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    owner = relationship("User", back_populates="urls")
    clicks = relationship(
        "Click", back_populates="url", cascade="all, delete-orphan"
    )
    qr_code = relationship("QRCode", back_populates="url", uselist=False)

    @property
    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at


class Click(Base):
    __tablename__ = "clicks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    url_id = Column(Integer, ForeignKey("urls.id"), nullable=False, index=True)
    clicked_at = Column(DateTime, default=datetime.utcnow, index=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    referer = Column(String(500), nullable=True)
    country = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    device_type = Column(String(20), nullable=True)
    browser = Column(String(50), nullable=True)
    os = Column(String(50), nullable=True)

    # Relationships
    url = relationship("URL", back_populates="clicks")


class QRCode(Base):
    __tablename__ = "qr_codes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    url_id = Column(Integer, ForeignKey("urls.id"), nullable=True)
    qr_data = Column(Text, nullable=False)
    foreground_color = Column(String(7), default="#000000")
    background_color = Column(String(7), default="#FFFFFF")
    style = Column(String(20), default="square")
    logo_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="qr_codes")
    url = relationship("URL", back_populates="qr_code")


class BioPage(Base):
    __tablename__ = "bio_pages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    slug = Column(String(50), unique=True, nullable=False, index=True)
    title = Column(String(100), nullable=False)
    bio = Column(Text, nullable=True)
    avatar_url = Column(String(500), nullable=True)
    theme = Column(String(20), default="default")
    views = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="bio_pages")
    links = relationship(
        "BioLink",
        back_populates="page",
        cascade="all, delete-orphan",
        order_by="BioLink.position",
    )


class BioLink(Base):
    __tablename__ = "bio_links"

    id = Column(Integer, primary_key=True, autoincrement=True)
    page_id = Column(Integer, ForeignKey("bio_pages.id"), nullable=False)
    title = Column(String(100), nullable=False)
    url = Column(String(500), nullable=False)
    icon = Column(String(50), nullable=True)
    position = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)

    page = relationship("BioPage", back_populates="links")
