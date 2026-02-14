

# Gosha Connections Platform — Полное ТЗ

---

## 1. Обзор архитектуры

```
┌────────────────────────────────────────────────────────────────────┐
│                        GOSHA PLATFORM                              │
├─────────────┬──────────────┬──────────────┬───────────────────────┤
│  PUBLIC     │  USER AREA   │  ADMIN AREA  │  API                  │
│             │              │              │                       │
│  /          │  /dashboard  │  /admin      │  /api/v1/auth/*       │
│  /features  │  /links      │  /admin/users│  /api/v1/links/*      │
│  /pricing   │  /analytics  │  /admin/links│  /api/v1/analytics/*  │
│  /about     │  /qr-codes   │  /admin/stats│  /api/v1/users/*      │
│  /login     │  /bio-links  │              │  /api/v1/admin/*      │
│  /register  │  /settings   │              │                       │
│             │  /profile    │              │                       │
└─────────────┴──────────────┴──────────────┴───────────────────────┘
         │                │               │
         ▼                ▼               ▼
    ┌─────────────────────────────────────────┐
    │            SQLite Database              │
    │                                         │
    │  users · urls · clicks · qr_codes      │
    │  bio_pages · bio_links · sessions      │
    └─────────────────────────────────────────┘
```

---

## 2. Структура проекта

```
gosha-platform/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app, middleware, startup
│   ├── config.py                  # Settings
│   ├── database.py                # SQLAlchemy engine, sessions
│   │
│   ├── models/                    # SQLAlchemy модели
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── url.py
│   │   ├── click.py
│   │   ├── qr_code.py
│   │   └── bio.py
│   │
│   ├── schemas/                   # Pydantic схемы
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── url.py
│   │   ├── analytics.py
│   │   └── admin.py
│   │
│   ├── api/                       # API роуты
│   │   ├── __init__.py
│   │   ├── router.py             # главный роутер
│   │   ├── auth.py               # /api/v1/auth
│   │   ├── links.py              # /api/v1/links
│   │   ├── analytics.py          # /api/v1/analytics
│   │   ├── users.py              # /api/v1/users
│   │   ├── qr.py                 # /api/v1/qr
│   │   ├── bio.py                # /api/v1/bio
│   │   └── admin.py              # /api/v1/admin
│   │
│   ├── services/                  # Бизнес-логика
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── link_service.py
│   │   ├── analytics_service.py
│   │   ├── qr_service.py
│   │   └── user_service.py
│   │
│   ├── core/                      # Ядро
│   │   ├── __init__.py
│   │   ├── security.py           # JWT, hashing
│   │   ├── dependencies.py       # get_current_user, require_admin
│   │   └── exceptions.py         # кастомные ошибки
│   │
│   ├── pages/                     # Роуты для HTML-страниц
│   │   ├── __init__.py
│   │   ├── public.py             # /, /features, /pricing, /about
│   │   ├── auth_pages.py         # /login, /register
│   │   ├── dashboard.py          # /dashboard
│   │   ├── links_pages.py        # /links, /link/{id}
│   │   ├── analytics_pages.py    # /analytics
│   │   ├── settings_pages.py     # /settings, /profile
│   │   └── admin_pages.py        # /admin/*
│   │
│   ├── templates/                 # Jinja2 шаблоны
│   │   ├── base.html             # базовый layout
│   │   ├── components/           # переиспользуемые компоненты
│   │   │   ├── navbar.html
│   │   │   ├── footer.html
│   │   │   ├── sidebar.html
│   │   │   ├── stats_card.html
│   │   │   ├── link_card.html
│   │   │   ├── modal.html
│   │   │   └── theme_toggle.html
│   │   ├── public/
│   │   │   ├── landing.html
│   │   │   ├── features.html
│   │   │   ├── pricing.html
│   │   │   └── about.html
│   │   ├── auth/
│   │   │   ├── login.html
│   │   │   └── register.html
│   │   ├── dashboard/
│   │   │   ├── index.html
│   │   │   ├── links.html
│   │   │   ├── link_detail.html
│   │   │   ├── analytics.html
│   │   │   ├── qr_codes.html
│   │   │   ├── bio_links.html
│   │   │   ├── settings.html
│   │   │   └── profile.html
│   │   └── admin/
│   │       ├── index.html
│   │       ├── users.html
│   │       ├── links.html
│   │       └── stats.html
│   │
│   └── static/
│       ├── css/
│       │   ├── variables.css     # CSS-переменные (темы)
│       │   ├── base.css          # базовые стили
│       │   ├── components.css    # стили компонентов
│       │   ├── landing.css       # стили лендинга
│       │   ├── dashboard.css     # стили дашборда
│       │   └── admin.css         # стили админки
│       ├── js/
│       │   ├── app.js            # общая логика
│       │   ├── auth.js           # авторизация
│       │   ├── theme.js          # переключение тем
│       │   ├── links.js          # работа со ссылками
│       │   ├── analytics.js      # графики
│       │   ├── carousel.js       # карусель на лендинге
│       │   └── admin.js          # админка
│       └── img/
│           ├── logo.svg
│           ├── hero-illustration.svg
│           └── icons/
│
├── tests/
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_links.py
│   ├── test_analytics.py
│   ├── test_admin.py
│   └── test_services.py
│
├── alembic/                       # миграции (опционально)
├── requirements.txt
├── .env
└── README.md
```

---

## 3. Дизайн-система — цвета и темы

### Цветовая палитра

```
LIGHT THEME (по умолчанию, как Bitly):

┌─────────────────────────────────────────────────────┐
│                                                     │
│   Background:  #FFFDF8  (тёплый белый)              │
│   Surface:     #FFFFFF  (карточки)                   │
│   Border:      #E8E2D9  (тёплый серый)              │
│                                                     │
│   Text:                                              │
│     Primary:   #0D2943  (тёмно-синий)               │
│     Secondary: #031F39  (ещё темнее)                │
│     Muted:     #6B7A8D  (серо-синий)                │
│                                                     │
│   Accent:                                            │
│     Primary:   #EE6123  (оранжевый, как у Bitly)    │
│     Hover:     #D4561F                               │
│     Light:     #FFF0E8  (фон акцентных блоков)      │
│                                                     │
│   Secondary accents:                                 │
│     Blue:      #2A5BD7                               │
│     Green:     #1DB954                               │
│     Purple:    #7B2FF7                               │
│     Pink:      #E91E8C                               │
│                                                     │
└─────────────────────────────────────────────────────┘


DARK THEME:

┌─────────────────────────────────────────────────────┐
│                                                     │
│   Background:  #031F39  (глубокий тёмно-синий)      │
│   Surface:     #0D2943  (карточки)                   │
│   Border:      #1A3A5C  (синяя рамка)              │
│                                                     │
│   Text:                                              │
│     Primary:   #FFFDF8  (тёплый белый)              │
│     Secondary: #C4CDD6                               │
│     Muted:     #6B8299                               │
│                                                     │
│   Accent:      #EE6123  (тот же оранжевый)          │
│   Accent Light:#1A2E3F                               │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### CSS Variables (`variables.css`)

```css
/* ============================================
   THEME SYSTEM
   ============================================ */

:root,
[data-theme="light"] {
    /* Backgrounds */
    --bg-primary: #FFFDF8;
    --bg-secondary: #F5F0E8;
    --bg-surface: #FFFFFF;
    --bg-surface-hover: #FBF8F3;
    --bg-elevated: #FFFFFF;

    /* Text */
    --text-primary: #0D2943;
    --text-secondary: #031F39;
    --text-muted: #6B7A8D;
    --text-inverse: #FFFDF8;

    /* Accent */
    --accent: #EE6123;
    --accent-hover: #D4561F;
    --accent-light: #FFF0E8;
    --accent-text: #FFFFFF;

    /* Borders */
    --border-default: #E8E2D9;
    --border-hover: #D1C9BD;
    --border-focus: #EE6123;

    /* Shadows */
    --shadow-sm: 0 1px 3px rgba(13, 41, 67, 0.06);
    --shadow-md: 0 4px 12px rgba(13, 41, 67, 0.08);
    --shadow-lg: 0 8px 30px rgba(13, 41, 67, 0.1);
    --shadow-xl: 0 16px 48px rgba(13, 41, 67, 0.12);

    /* Status */
    --success: #1DB954;
    --success-light: #E8F8EE;
    --warning: #F5A623;
    --warning-light: #FFF8E8;
    --error: #E53E3E;
    --error-light: #FDE8E8;
    --info: #2A5BD7;
    --info-light: #E8F0FF;

    /* Metrics cards gradient backgrounds */
    --gradient-1: linear-gradient(135deg, #EE6123 0%, #E91E8C 100%);
    --gradient-2: linear-gradient(135deg, #2A5BD7 0%, #7B2FF7 100%);
    --gradient-3: linear-gradient(135deg, #1DB954 0%, #00B4D8 100%);
    --gradient-4: linear-gradient(135deg, #F5A623 0%, #EE6123 100%);

    /* Radius */
    --radius-xs: 6px;
    --radius-sm: 10px;
    --radius-md: 14px;
    --radius-lg: 20px;
    --radius-xl: 28px;
    --radius-full: 9999px;

    /* Navbar */
    --navbar-bg: rgba(255, 253, 248, 0.85);
    --navbar-blur: blur(20px);
    --navbar-border: #E8E2D9;
    --navbar-height: 72px;

    /* Sidebar */
    --sidebar-width: 260px;
    --sidebar-bg: #FFFFFF;
    --sidebar-border: #E8E2D9;

    /* Transitions */
    --transition-fast: 0.15s ease;
    --transition-normal: 0.3s ease;
    --transition-slow: 0.5s cubic-bezier(0.16, 1, 0.3, 1);
}


[data-theme="dark"] {
    --bg-primary: #031F39;
    --bg-secondary: #06273F;
    --bg-surface: #0D2943;
    --bg-surface-hover: #12334F;
    --bg-elevated: #143A5A;

    --text-primary: #FFFDF8;
    --text-secondary: #C4CDD6;
    --text-muted: #6B8299;
    --text-inverse: #031F39;

    --accent: #EE6123;
    --accent-hover: #F57842;
    --accent-light: #1A2E3F;
    --accent-text: #FFFFFF;

    --border-default: #1A3A5C;
    --border-hover: #2A4D6E;
    --border-focus: #EE6123;

    --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.2);
    --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.25);
    --shadow-lg: 0 8px 30px rgba(0, 0, 0, 0.3);
    --shadow-xl: 0 16px 48px rgba(0, 0, 0, 0.35);

    --success-light: #0A2A1A;
    --warning-light: #2A2210;
    --error-light: #2A1010;
    --info-light: #0A1A2A;

    --navbar-bg: rgba(3, 31, 57, 0.85);
    --navbar-border: #1A3A5C;

    --sidebar-bg: #0D2943;
    --sidebar-border: #1A3A5C;
}


/* Transition для смены темы */
[data-theme-transition] * {
    transition:
        background-color 0.4s ease,
        color 0.3s ease,
        border-color 0.3s ease,
        box-shadow 0.3s ease !important;
}
```

---

## 4. База данных — модели

### Диаграмма связей

```
┌─────────────┐       ┌──────────────┐       ┌──────────────┐
│   users     │       │     urls     │       │    clicks    │
├─────────────┤       ├──────────────┤       ├──────────────┤
│ id (PK)     │──┐    │ id (PK)      │──┐    │ id (PK)      │
│ email       │  │    │ user_id (FK) │  │    │ url_id (FK)  │
│ username    │  └───▶│ original_url │  └───▶│ clicked_at   │
│ password    │       │ short_code   │       │ ip_address   │
│ role        │       │ title        │       │ user_agent   │
│ avatar_url  │       │ is_active    │       │ referer      │
│ created_at  │       │ expires_at   │       │ country      │
│ is_active   │       │ clicks_count │       │ device_type  │
│ theme_pref  │       │ created_at   │       │ browser      │
└─────────────┘       │ updated_at   │       └──────────────┘
       │              └──────────────┘
       │
       │         ┌──────────────┐       ┌──────────────┐
       │         │  qr_codes    │       │  bio_pages   │
       │         ├──────────────┤       ├──────────────┤
       │         │ id (PK)      │       │ id (PK)      │
       └────────▶│ user_id (FK) │       │ user_id (FK) │◀──┐
                 │ url_id (FK)  │       │ slug         │   │
                 │ qr_data      │       │ title        │   │
                 │ style_config │       │ bio          │   │
                 │ created_at   │       │ theme        │   │
                 └──────────────┘       │ created_at   │   │
                                        └──────────────┘   │
                                               │           │
                                        ┌──────────────┐   │
                                        │  bio_links   │   │
                                        ├──────────────┤   │
                                        │ id (PK)      │   │
                                        │ page_id (FK) │───┘
                                        │ title        │
                                        │ url          │
                                        │ icon         │
                                        │ position     │
                                        │ clicks       │
                                        └──────────────┘
```

### SQLAlchemy модели

```python
# app/models/user.py

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum
from sqlalchemy.orm import relationship
from app.database import Base
import enum


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
    theme_preference = Column(String(10), default="light")  # light / dark

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    # Relationships
    urls = relationship("URL", back_populates="owner", cascade="all, delete-orphan")
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
```

```python
# app/models/url.py

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base


class URL(Base):
    __tablename__ = "urls"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    original_url = Column(Text, nullable=False)
    short_code = Column(String(20), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=True)  # пользователь может дать название
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime, nullable=True)  # опциональный срок действия
    clicks_count = Column(Integer, default=0)
    tags = Column(String(500), nullable=True)  # JSON массив тегов

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    owner = relationship("User", back_populates="urls")
    clicks = relationship("Click", back_populates="url", cascade="all, delete-orphan")
    qr_code = relationship("QRCode", back_populates="url", uselist=False)

    @property
    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at
```

```python
# app/models/click.py

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


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
    device_type = Column(String(20), nullable=True)  # mobile / desktop / tablet
    browser = Column(String(50), nullable=True)
    os = Column(String(50), nullable=True)

    # Relationships
    url = relationship("URL", back_populates="clicks")
```

```python
# app/models/qr_code.py

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base


class QRCode(Base):
    __tablename__ = "qr_codes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    url_id = Column(Integer, ForeignKey("urls.id"), nullable=True)
    qr_data = Column(Text, nullable=False)  # base64 PNG
    foreground_color = Column(String(7), default="#000000")
    background_color = Column(String(7), default="#FFFFFF")
    style = Column(String(20), default="square")  # square / rounded / dots
    logo_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="qr_codes")
    url = relationship("URL", back_populates="qr_code")
```

```python
# app/models/bio.py

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base


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
    links = relationship("BioLink", back_populates="page",
                         cascade="all, delete-orphan",
                         order_by="BioLink.position")


class BioLink(Base):
    __tablename__ = "bio_links"

    id = Column(Integer, primary_key=True, autoincrement=True)
    page_id = Column(Integer, ForeignKey("bio_pages.id"), nullable=False)
    title = Column(String(100), nullable=False)
    url = Column(String(500), nullable=False)
    icon = Column(String(50), nullable=True)  # emoji или icon name
    position = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)

    page = relationship("BioPage", back_populates="links")
```

---

## 5. Система авторизации — JWT

### `core/security.py`

```python
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Access token — короткоживущий (30 минут).
    Хранится в httpOnly cookie.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({
        "exp": expire,
        "type": "access"
    })
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(data: dict) -> str:
    """
    Refresh token — долгоживущий (7 дней).
    Тоже в httpOnly cookie.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({
        "exp": expire,
        "type": "refresh"
    })
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    """Декодировать и проверить JWT."""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None
```

### `core/dependencies.py`

```python
from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.core.security import decode_token


async def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
) -> User:
    """
    Dependency: извлекает текущего пользователя из cookie.
    Для API: можно также поддержать Bearer header.
    """
    # Пробуем cookie
    token = request.cookies.get("access_token")

    # Пробуем Authorization header (для API-клиентов)
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Не авторизован",
        )

    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалидный токен",
        )

    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден или деактивирован",
        )

    return user


async def get_current_user_optional(
    request: Request,
    db: Session = Depends(get_db),
) -> User | None:
    """То же, но не кидает ошибку — для страниц, которые работают и без авторизации."""
    try:
        return await get_current_user(request, db)
    except HTTPException:
        return None


async def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """Dependency: только для админов."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Требуются права администратора",
        )
    return current_user
```

### `api/auth.py`

```python
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Response, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, UserRole
from app.schemas.auth import (
    RegisterRequest, LoginRequest, TokenResponse, UserResponse
)
from app.core.security import (
    hash_password, verify_password,
    create_access_token, create_refresh_token, decode_token
)
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(
    data: RegisterRequest,
    response: Response,
    db: Session = Depends(get_db),
):
    """Регистрация нового пользователя."""
    # Проверяем уникальность
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=409, detail="Email уже зарегистрирован")

    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(status_code=409, detail="Username уже занят")

    # Создаём пользователя
    user = User(
        email=data.email,
        username=data.username,
        hashed_password=hash_password(data.password),
        role=UserRole.USER,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Генерируем токены
    _set_auth_cookies(response, user)

    return UserResponse.model_validate(user)


@router.post("/login", response_model=UserResponse)
async def login(
    data: LoginRequest,
    response: Response,
    db: Session = Depends(get_db),
):
    """Вход в систему."""
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Неверный email или пароль")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Аккаунт деактивирован")

    # Обновляем last_login
    user.last_login = datetime.utcnow()
    db.commit()

    _set_auth_cookies(response, user)

    return UserResponse.model_validate(user)


@router.post("/logout")
async def logout(response: Response):
    """Выход — удаляем cookies."""
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/")
    return {"detail": "Успешный выход"}


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    """Обновление access token через refresh token."""
    refresh = request.cookies.get("refresh_token")
    if not refresh:
        raise HTTPException(status_code=401, detail="Refresh token отсутствует")

    payload = decode_token(refresh)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Невалидный refresh token")

    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    if not user:
        raise HTTPException(status_code=401, detail="Пользователь не найден")

    _set_auth_cookies(response, user)

    return {"detail": "Токен обновлён"}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Получить данные текущего пользователя."""
    return UserResponse.model_validate(current_user)


def _set_auth_cookies(response: Response, user: User):
    """Устанавливаем httpOnly cookies с токенами."""
    access = create_access_token(data={"sub": str(user.id), "role": user.role})
    refresh = create_refresh_token(data={"sub": str(user.id)})

    response.set_cookie(
        key="access_token",
        value=access,
        httponly=True,
        secure=False,  # True в продакшне (HTTPS)
        samesite="lax",
        max_age=30 * 60,  # 30 минут
        path="/",
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=7 * 24 * 60 * 60,  # 7 дней
        path="/",
    )
```

### Pydantic схемы для авторизации

```python
# app/schemas/auth.py

from pydantic import BaseModel, EmailStr, field_validator
import re


class RegisterRequest(BaseModel):
    email: EmailStr
    username: str
    password: str

    @field_validator("username")
    @classmethod
    def validate_username(cls, v):
        if not re.match(r"^[a-zA-Z0-9_]{3,30}$", v):
            raise ValueError("Username: 3-30 символов, буквы, цифры, подчёркивание")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Пароль минимум 8 символов")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Пароль должен содержать заглавную букву")
        if not re.search(r"[0-9]", v):
            raise ValueError("Пароль должен содержать цифру")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    detail: str


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    role: str
    avatar_url: str | None
    theme_preference: str
    created_at: str

    class Config:
        from_attributes = True
```

---

## 6. Все страницы — детальное описание

### Карта навигации

```
┌─────────────────────────────────────────────────────────────────┐
│                     НАВИГАЦИЯ (HEADER)                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  PUBLIC NAVBAR (неавторизован):                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ 🔗 Gosha │ Features │ Pricing │ About │ [Login] [SignUp] │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                 │
│  USER NAVBAR (авторизован):                                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ 🔗 Gosha │ Dashboard │ Links │ Analytics │ QR │ Bio │    │   │
│  │          │           │       │           │    │     │    │   │
│  │          │                    [🌙/☀️] [Avatar ▾]         │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                 │
│  DASHBOARD SIDEBAR (боковое меню):                              │
│  ┌────────────────┐                                             │
│  │ 📊 Dashboard   │                                             │
│  │ 🔗 Links       │                                             │
│  │ 📈 Analytics   │                                             │
│  │ 📱 QR Codes    │                                             │
│  │ 🌐 Bio Links   │                                             │
│  │ ─────────────  │                                             │
│  │ ⚙️  Settings   │                                             │
│  │ 👤 Profile     │                                             │
│  │ ─────────────  │                                             │
│  │ 🛡️  Admin      │ ← только для role=admin                    │
│  └────────────────┘                                             │
└─────────────────────────────────────────────────────────────────┘
```

---

### СТРАНИЦА 1: Landing (`/`)

```
┌─────────────────────────────────────────────────────────────────────┐
│ NAVBAR: 🔗 Gosha    Features  Pricing  About    [Login] [Sign Up]  │
│ ─────────────────────────────────────────────────────────────────── │
│                                                                     │
│                    HERO SECTION                                     │
│                                                                     │
│              Build stronger digital                                 │
│                 connections                                          │
│                                                                     │
│    Use our URL shortener, QR Codes, and landing pages               │
│    to engage your audience and connect them to the                  │
│    right information.                                                │
│                                                                     │
│    ┌──────────────────┐  ┌──────────────────┐                       │
│    │ ✨ Get Started   │  │  Learn More  →   │                       │
│    │    for Free      │  │                  │                       │
│    └──────────────────┘  └──────────────────┘                       │
│                                                                     │
│    [Hero Illustration: абстрактная графика с линками]               │
│                                                                     │
│ ─────────────────────────────────────────────────────────────────── │
│                                                                     │
│           Great Connections Start with a                             │
│              click OR scan                                          │
│                                                                     │
│    ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐     │
│    │ 🔗         │ │ 📱         │ │ 🌐         │ │ 📊         │     │
│    │ URL        │ │ QR Codes   │ │ Bio Links  │ │ Analytics  │     │
│    │ Shortener  │ │            │ │            │ │            │     │
│    │            │ │ Create QR  │ │ Build your │ │ Track and  │     │
│    │ Shorten    │ │ codes that │ │ micro-site │ │ analyze    │     │
│    │ your URLs  │ │ connect    │ │ with all   │ │ every      │     │
│    │ and share  │ │ to any     │ │ your links │ │ connection │     │
│    │ everywhere │ │ content    │ │ in one     │ │ you make   │     │
│    │            │ │            │ │ place      │ │            │     │
│    │ [Learn →]  │ │ [Learn →]  │ │ [Learn →]  │ │ [Learn →]  │     │
│    └────────────┘ └────────────┘ └────────────┘ └────────────┘     │
│                                                                     │
│ ─────────────────────────────────────────────────────────────────── │
│                                                                     │
│        The Gosha Connections Platform                                │
│                                                                     │
│    All the products you need to build brand connections,            │
│    manage links and connect with audiences everywhere,              │
│    in a single unified platform.                                    │
│                                                                     │
│    ┌──────────────────────────────────────────────────────────┐     │
│    │  [Animated platform preview / mockup / illustration]     │     │
│    └──────────────────────────────────────────────────────────┘     │
│                                                                     │
│ ─────────────────────────────────────────────────────────────────── │
│                                                                     │
│    Adopted and loved by millions of users for over a decade         │
│                                                                     │
│    ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│    │  600K+   │  │  256M    │  │  800+    │  │  10B     │         │
│    │ Global   │  │ Links &  │  │ App      │  │ Clicks & │         │
│    │ paying   │  │ QR Codes │  │ integra- │  │ scans    │         │
│    │customers │  │ created  │  │ tions    │  │ monthly  │         │
│    │          │  │ monthly  │  │          │  │          │         │
│    └──────────┘  └──────────┘  └──────────┘  └──────────┘         │
│         ▲              ▲             ▲              ▲               │
│    Анимация: числа "набегают" от 0 до значения при скролле         │
│                                                                     │
│ ─────────────────────────────────────────────────────────────────── │
│                                                                     │
│          What our customers are saying                               │
│                                                                     │
│    ┌──────────────┐ ┌──────────────┐ ┌──────────────┐              │
│    │ ⭐⭐⭐⭐⭐    │ │ ⭐⭐⭐⭐⭐    │ │ ⭐⭐⭐⭐⭐    │              │
│    │              │ │              │ │              │              │
│    │ "Gosha has   │ │ "Best URL    │ │ "Analytics   │              │
│    │  completely  │ │  shortener   │ │  features    │              │
│    │  changed how │ │  we've ever  │ │  are         │              │
│    │  we share    │ │  used..."    │ │  incredible" │              │
│    │  content"    │ │              │ │              │              │
│    │              │ │  — Jane D.   │ │  — Mike T.   │              │
│    │  — Alex K.   │ │  Marketing   │ │  Growth Lead │              │
│    │  CEO, Tech   │ │              │ │              │              │
│    └──────────────┘ └──────────────┘ └──────────────┘              │
│                                                                     │
│ ─────────────────────────────────────────────────────────────────── │
│                                                                     │
│       See how other businesses use Gosha                            │
│                                                                     │
│    ◀  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────  ▶         │
│       │  🏢      │ │  🛍️      │ │  🎓      │ │  🏥                │
│       │ Enterprise│ │ E-commerce│ │ Education│ │ Health             │
│       │          │ │          │ │          │ │                     │
│       │ See how  │ │ Boost    │ │ Share    │ │ ...                 │
│       │ Fortune  │ │ CTR by   │ │ learning │ │                     │
│       │ 500 use  │ │ 34% with │ │ resources│ │                     │
│       │ Gosha    │ │ branded  │ │ easily   │ │                     │
│       │ links    │ │ links    │ │          │ │                     │
│       │          │ │          │ │          │ │                     │
│       │ [Read →] │ │ [Read →] │ │ [Read →] │ │                     │
│       └──────────┘ └──────────┘ └──────────┘ └────────             │
│                                                                     │
│    Стрелки ◀ ▶ — красивые круглые кнопки, карусель                 │
│    с плавной CSS-анимацией scroll-snap                              │
│                                                                     │
│ ─────────────────────────────────────────────────────────────────── │
│                                                                     │
│          More than a link shortener                                  │
│                                                                     │
│    Knowing how your clicks and scans are performing                 │
│    should be as easy as making them. Track, analyze,                │
│    and optimize all your connections in one place.                   │
│                                                                     │
│              ┌───────────────────────┐                               │
│              │  ✨ Get Started Free  │                               │
│              └───────────────────────┘                               │
│                                                                     │
│ ─────────────────────────────────────────────────────────────────── │
│                         FOOTER                                      │
│  🔗 Gosha Platform                                                  │
│                                                                     │
│  Products     │  Resources   │  Company     │  Legal               │
│  URL Shorter  │  Blog        │  About       │  Privacy             │
│  QR Codes     │  Help Center │  Careers     │  Terms               │
│  Bio Links    │  API Docs    │  Contact     │  Cookie Policy       │
│  Analytics    │  Status      │  Press       │                      │
│                                                                     │
│  ─────────────────────────────────────────────────────────────      │
│  © 2024 Gosha · Made by ternopolskiy                                │
│  GitHub: github.com/ternopolskiy                                    │
└─────────────────────────────────────────────────────────────────────┘
```

---

### СТРАНИЦА 2: Login (`/login`)

```
┌─────────────────────────────────────────────────────────────┐
│ NAVBAR (public)                                             │
│ ───────────────────────────────────────────────────────────  │
│                                                             │
│  Фон: #FFFDF8 с тонким паттерном / градиентом              │
│                                                             │
│         ┌────────────────────────────────────┐              │
│         │         GLASS CARD                 │              │
│         │    border-radius: 28px             │              │
│         │    shadow: xl                      │              │
│         │                                    │              │
│         │    🔗 Welcome back                 │              │
│         │    Log in to your Gosha account    │              │
│         │                                    │              │
│         │    ┌──────────────────────────┐    │              │
│         │    │ 📧  Email                │    │              │
│         │    └──────────────────────────┘    │              │
│         │                                    │              │
│         │    ┌──────────────────────────┐    │              │
│         │    │ 🔒  Password      [👁️]   │    │              │
│         │    └──────────────────────────┘    │              │
│         │                                    │              │
│         │    ☐ Remember me    Forgot pass?   │              │
│         │                                    │              │
│         │    ┌──────────────────────────┐    │              │
│         │    │    ✨ Log In             │    │              │
│         │    └──────────────────────────┘    │              │
│         │                                    │              │
│         │    ──────── or ────────            │              │
│         │                                    │              │
│         │    ┌──────────────────────────┐    │              │
│         │    │  🔵 Continue with Google │    │              │
│         │    └──────────────────────────┘    │              │
│         │    ┌──────────────────────────┐    │              │
│         │    │  ⚫ Continue with GitHub │    │              │
│         │    └──────────────────────────┘    │              │
│         │                                    │              │
│         │    Don't have an account?          │              │
│         │    Sign up for free →              │              │
│         │                                    │              │
│         └────────────────────────────────────┘              │
│                                                             │
│  FOOTER                                                     │
└─────────────────────────────────────────────────────────────┘
```

---

### СТРАНИЦА 3: Register (`/register`)

```
Аналогичен Login, но с полями:
- Username
- Email  
- Password (с индикатором силы пароля)
- Confirm Password
- ☐ I agree to Terms of Service

Индикатор силы пароля:
┌──────────────────────────────────────┐
│  Password strength:                  │
│  ████████░░░░░░░░░░░░  Medium        │
│                                      │
│  ✅ 8+ characters                    │
│  ✅ Uppercase letter                 │
│  ❌ Number                           │
│  ❌ Special character                │
└──────────────────────────────────────┘
```

---

### СТРАНИЦА 4: Features (`/features`)

```
┌─────────────────────────────────────────────────────────────────┐
│ NAVBAR                                                          │
│ ─────────────────────────────────────────────────────────────── │
│                                                                 │
│   HERO:  Powerful features for                                  │
│          powerful connections                                    │
│                                                                 │
│   ────────────────────────────────────────────────────────────  │
│                                                                 │
│   Feature 1: URL Shortener                                      │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  [Illustration]  │  Shorten, brand, and track           │   │
│   │                  │  every link you share.               │   │
│   │                  │                                      │   │
│   │                  │  • Custom branded links               │   │
│   │                  │  • Link expiration dates              │   │
│   │                  │  • UTM parameter builder              │   │
│   │                  │  • Bulk link creation                 │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│   Feature 2: QR Code Generator                                  │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  Customizable QR codes  │  [Illustration]               │   │
│   │  that match your brand  │                               │   │
│   │                         │                               │   │
│   │  • Custom colors         │                               │   │
│   │  • Logo embedding        │                               │   │
│   │  • Multiple styles       │                               │   │
│   │  • Download PNG/SVG      │                               │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│   Feature 3: Bio Links (как Linktree)                           │
│   Feature 4: Advanced Analytics                                 │
│   Feature 5: Team Collaboration                                 │
│                                                                 │
│   CTA: Ready to get started?                                    │
│   [Get Started Free]                                            │
│                                                                 │
│   FOOTER                                                        │
└─────────────────────────────────────────────────────────────────┘
```

---

### СТРАНИЦА 5: Pricing (`/pricing`)

```
┌─────────────────────────────────────────────────────────────────┐
│ NAVBAR                                                          │
│ ─────────────────────────────────────────────────────────────── │
│                                                                 │
│   Choose the right plan for you                                 │
│   [Monthly ○─● Annual (save 20%)]                               │
│                                                                 │
│   ┌──────────────┐ ┌──────────────────┐ ┌──────────────┐       │
│   │    FREE      │ │  ⭐ PRO          │ │  ENTERPRISE  │       │
│   │              │ │  Most Popular     │ │              │       │
│   │   $0/mo      │ │   $8/mo          │ │  Custom      │       │
│   │              │ │                   │ │              │       │
│   │ • 50 links   │ │ • 500 links      │ │ • Unlimited  │       │
│   │ • Basic      │ │ • Custom domains │ │ • SSO        │       │
│   │   analytics  │ │ • Advanced       │ │ • API access │       │
│   │ • 1 QR code  │ │   analytics      │ │ • SLA        │       │
│   │ • 1 Bio page │ │ • 100 QR codes   │ │ • Dedicated  │       │
│   │              │ │ • 5 Bio pages    │ │   support    │       │
│   │              │ │ • Priority       │ │              │       │
│   │              │ │   support        │ │              │       │
│   │              │ │                   │ │              │       │
│   │ [Get Started]│ │ [Start Free     ]│ │ [Contact Us ]│       │
│   │              │ │ [Trial          ]│ │              │       │
│   └──────────────┘ └──────────────────┘ └──────────────┘       │
│                                                                 │
│   FAQ accordion:                                                │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │ ▶ What happens when I exceed my link limit?             │  │
│   │ ▶ Can I upgrade or downgrade at any time?               │  │
│   │ ▶ Is there a free trial for Pro?                        │  │
│   │ ▼ Do you offer refunds?                                 │  │
│   │   Yes, we offer a 30-day money-back guarantee...        │  │
│   └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│   FOOTER                                                        │
└─────────────────────────────────────────────────────────────────┘
```

---

### СТРАНИЦА 6: About (`/about`)

```
Team section с фото, миссия компании, 
timeline истории, партнёры, CTA.
```

---

### СТРАНИЦА 7: Dashboard (`/dashboard`) — ГЛАВНАЯ ДЛЯ ЗАЛОГИНЕННЫХ

```
┌─────────────────────────────────────────────────────────────────────────┐
│ NAVBAR: 🔗 Gosha   Dashboard  Links  Analytics  QR  Bio  [🌙] [👤▾]  │
│ ─────────────────────────────────────────────────────────────────────── │
│                                                                         │
│ ┌──────────┐  ┌─────────────────────────────────────────────────────┐  │
│ │ SIDEBAR  │  │                                                     │  │
│ │          │  │   Good morning, Alex! 👋                            │  │
│ │ 📊 Dash  │  │                                                     │  │
│ │ 🔗 Links │  │   METRIC CARDS (4 штуки в ряд):                    │  │
│ │ 📈 Anlyt │  │   ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────┐ │  │
│ │ 📱 QR    │  │   │ gradient │ │ gradient │ │ gradient │ │ grad │ │  │
│ │ 🌐 Bio   │  │   │ bg #1    │ │ bg #2    │ │ bg #3    │ │ #4   │ │  │
│ │ ──────── │  │   │          │ │          │ │          │ │      │ │  │
│ │ ⚙️ Sets  │  │   │  47      │ │  1,234   │ │  89%     │ │  12  │ │  │
│ │ 👤 Prof  │  │   │ Total    │ │ Total    │ │ Click    │ │ QR   │ │  │
│ │ ──────── │  │   │ Links    │ │ Clicks   │ │ Rate     │ │ Codes│ │  │
│ │ 🛡️ Admin │  │   │          │ │ ↑ 12%    │ │ ↑ 3%    │ │      │ │  │
│ │          │  │   └──────────┘ └──────────┘ └──────────┘ └──────┘ │  │
│ │          │  │                                                     │  │
│ │          │  │   ─────────────────────────────────────────────────  │  │
│ │          │  │                                                     │  │
│ │          │  │   QUICK SHORTEN (форма сокращения):                 │  │
│ │          │  │   ┌──────────────────────────────────┐ ┌──────────┐ │  │
│ │          │  │   │ 🔗  Paste a long URL...          │ │ Shorten  │ │  │
│ │          │  │   └──────────────────────────────────┘ └──────────┘ │  │
│ │          │  │   ┌────────────────┐ ┌────────────────┐             │  │
│ │          │  │   │ Custom alias   │ │ Expiration ▾   │             │  │
│ │          │  │   └────────────────┘ └────────────────┘             │  │
│ │          │  │                                                     │  │
│ │          │  │   ─────────────────────────────────────────────────  │  │
│ │          │  │                                                     │  │
│ │          │  │   CLICKS CHART (последние 30 дней):                 │  │
│ │          │  │   ┌──────────────────────────────────────────────┐  │  │
│ │          │  │   │  📈                                          │  │  │
│ │          │  │   │      ╱╲    ╱╲                                │  │  │
│ │          │  │   │     ╱  ╲  ╱  ╲      ╱╲                      │  │  │
│ │          │  │   │    ╱    ╲╱    ╲    ╱  ╲                     │  │  │
│ │          │  │   │   ╱              ╲╱    ╲                    │  │  │
│ │          │  │   │  ╱                      ╲                   │  │  │
│ │          │  │   │ ╱                                           │  │  │
│ │          │  │   └──────────────────────────────────────────────┘  │  │
│ │          │  │   [7d] [30d] [90d] [1y]    Line │ Bar              │  │
│ │          │  │                                                     │  │
│ │          │  │   ─────────────────────────────────────────────────  │  │
│ │          │  │                                                     │  │
│ │          │  │   RECENT LINKS (последние 5):                       │  │
│ │          │  │   ┌──────────────────────────────────────────────┐  │  │
│ │          │  │   │ 🔗 gosha.link/abc123                        │  │  │
│ │          │  │   │   → google.com/very/long/url...              │  │  │
│ │          │  │   │   Created 2h ago · 34 clicks    [📋] [📈]  │  │  │
│ │          │  │   ├──────────────────────────────────────────────┤  │  │
│ │          │  │   │ 🔗 gosha.link/my-blog                       │  │  │
│ │          │  │   │   → medium.com/@alex/my-article              │  │  │
│ │          │  │   │   Created 1d ago · 128 clicks   [📋] [📈]  │  │  │
│ │          │  │   └──────────────────────────────────────────────┘  │  │
│ │          │  │   [View all links →]                                │  │
│ │          │  │                                                     │  │
│ └──────────┘  └─────────────────────────────────────────────────────┘  │
│                                                                         │
│ FOOTER                                                                  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

### СТРАНИЦА 8: Links (`/links`)

```
┌─ SIDEBAR ──┐  ┌──────────────────────────────────────────────────┐
│             │  │                                                  │
│             │  │  My Links                                 [+ New]│
│             │  │                                                  │
│             │  │  Search: ┌──────────────────────┐               │
│             │  │          │ 🔍 Search links...    │               │
│             │  │          └──────────────────────┘               │
│             │  │                                                  │
│             │  │  Filters: [All ▾] [Active ▾] [Sort: Newest ▾]   │
│             │  │                                                  │
│             │  │  ┌───────────────────────────────────────────┐   │
│             │  │  │ ☐ │ 🔗 gosha.link/abc123    │ 34 clicks  │   │
│             │  │  │   │ → google.com/...         │ 2h ago     │   │
│             │  │  │   │ Tags: [marketing] [social]│           │   │
│             │  │  │   │                          │ [···]      │   │
│             │  │  ├───────────────────────────────────────────┤   │
│             │  │  │ ☐ │ 🔗 gosha.link/my-blog   │ 128 clicks │   │
│             │  │  │   │ → medium.com/...          │ 1d ago     │   │
│             │  │  │   │ Tags: [blog]              │           │   │
│             │  │  │   │                          │ [···]      │   │
│             │  │  ├───────────────────────────────────────────┤   │
│             │  │  │ ...                                       │   │
│             │  │  └───────────────────────────────────────────┘   │
│             │  │                                                  │
│             │  │  Pagination: ◀ 1 2 3 ... 12 ▶                   │
│             │  │                                                  │
│             │  │  Bulk actions (когда выбраны):                   │
│             │  │  ┌──────────────────────────────────────────┐    │
│             │  │  │ 3 selected: [🗑 Delete] [📋 Export] [⏸ Disable]│
│             │  │  └──────────────────────────────────────────┘    │
│             │  │                                                  │
└─────────────┘  └──────────────────────────────────────────────────┘

Кнопка [···] при нажатии показывает dropdown:
┌──────────────────┐
│ 📋 Copy link     │
│ ✏️  Edit          │
│ 📊 Analytics     │
│ 📱 QR Code       │
│ ⏸  Disable       │
│ ──────────────── │
│ 🗑  Delete        │ ← красный
└──────────────────┘
```

---

### СТРАНИЦА 9: Link Detail (`/link/{id}`)

```
┌─ SIDEBAR ──┐  ┌──────────────────────────────────────────────────┐
│             │  │                                                  │
│             │  │  ← Back to links                                │
│             │  │                                                  │
│             │  │  gosha.link/my-blog                              │
│             │  │  → medium.com/@alex/my-long-article-about-tech   │
│             │  │  Created Dec 15, 2024 · Active                   │
│             │  │                                                  │
│             │  │  [📋 Copy] [✏️ Edit] [📱 QR] [⏸ Disable]        │
│             │  │                                                  │
│             │  │  ─────────────────────────────────────────────── │
│             │  │                                                  │
│             │  │  Metrics:                                        │
│             │  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐   │
│             │  │  │  128   │ │  45    │ │  67%   │ │  3.2s  │   │
│             │  │  │ Total  │ │ Today  │ │ CTR    │ │ Avg    │   │
│             │  │  │ Clicks │ │ Clicks │ │        │ │ Time   │   │
│             │  │  └────────┘ └────────┘ └────────┘ └────────┘   │
│             │  │                                                  │
│             │  │  Clicks over time (Chart.js / ApexCharts):       │
│             │  │  ┌──────────────────────────────────────────┐   │
│             │  │  │  📈 Area chart with gradient fill        │   │
│             │  │  │                                          │   │
│             │  │  └──────────────────────────────────────────┘   │
│             │  │                                                  │
│             │  │  ┌─────────────────┐ ┌─────────────────────┐   │
│             │  │  │ Top Referrers   │ │ Devices             │   │
│             │  │  │                 │ │                     │   │
│             │  │  │ twitter.com  45%│ │  🖥 Desktop   62%   │   │
│             │  │  │ google.com   30%│ │  📱 Mobile    31%   │   │
│             │  │  │ direct       20%│ │  📱 Tablet     7%   │   │
│             │  │  │ facebook.com  5%│ │                     │   │
│             │  │  └─────────────────┘ └─────────────────────┘   │
│             │  │                                                  │
│             │  │  ┌─────────────────┐ ┌─────────────────────┐   │
│             │  │  │ Browsers        │ │ Countries           │   │
│             │  │  │                 │ │                     │   │
│             │  │  │ Chrome    58%   │ │ 🇷🇺 Russia    40%   │   │
│             │  │  │ Safari    22%   │ │ 🇺🇸 USA       25%   │   │
│             │  │  │ Firefox   12%   │ │ 🇩🇪 Germany   15%   │   │
│             │  │  │ Edge       8%   │ │ 🇬🇧 UK        10%   │   │
│             │  │  └─────────────────┘ └─────────────────────┘   │
│             │  │                                                  │
└─────────────┘  └──────────────────────────────────────────────────┘
```

---

### СТРАНИЦА 10: Analytics (`/analytics`)

```
Общая аналитика по ВСЕМ ссылкам пользователя:

- Графики кликов за период (7d / 30d / 90d / 1y / custom)
- Top-5 ссылок по кликам
- Географическая карта кликов (heatmap)
- Распределение по устройствам (donut chart)
- Распределение по браузерам (donut chart)  
- Топ рефереров (bar chart)
- Активность по часам суток (heatmap)
- Экспорт в CSV
```

---

### СТРАНИЦА 11: QR Codes (`/qr-codes`)

```
┌─ SIDEBAR ──┐  ┌──────────────────────────────────────────────────┐
│             │  │                                                  │
│             │  │  QR Codes                              [+ New]   │
│             │  │                                                  │
│             │  │  Grid view / List view toggle                    │
│             │  │                                                  │
│             │  │  ┌──────────┐ ┌──────────┐ ┌──────────┐        │
│             │  │  │ ┌──────┐ │ │ ┌──────┐ │ │ ┌──────┐ │        │
│             │  │  │ │ QR   │ │ │ │ QR   │ │ │ │ QR   │ │        │
│             │  │  │ │ CODE │ │ │ │ CODE │ │ │ │ CODE │ │        │
│             │  │  │ │ IMG  │ │ │ │ IMG  │ │ │ │ IMG  │ │        │
│             │  │  │ └──────┘ │ │ └──────┘ │ │ └──────┘ │        │
│             │  │  │ My Blog  │ │ Portfolio│ │ Resume   │        │
│             │  │  │ 34 scans │ │ 12 scans │ │ 8 scans  │        │
│             │  │  │ [⬇] [✏️] │ │ [⬇] [✏️] │ │ [⬇] [✏️] │        │
│             │  │  └──────────┘ └──────────┘ └──────────┘        │
│             │  │                                                  │
│             │  │  QR Creator Modal:                               │
│             │  │  ┌──────────────────────────────────────────┐   │
│             │  │  │ Select a link:  [dropdown]               │   │
│             │  │  │ Style:          ○ Square ○ Rounded ○ Dots│   │
│             │  │  │ Foreground:     [#000000] 🎨             │   │
│             │  │  │ Background:     [#FFFFFF] 🎨             │   │
│             │  │  │ Logo:           [Upload]                 │   │
│             │  │  │                                          │   │
│             │  │  │ Preview:  ┌──────┐                       │   │
│             │  │  │           │ LIVE │                       │   │
│             │  │  │           │  QR  │                       │   │
│             │  │  │           └──────┘                       │   │
│             │  │  │                                          │   │
│             │  │  │ [Download PNG] [Download SVG] [Create]   │   │
│             │  │  └──────────────────────────────────────────┘   │
│             │  │                                                  │
└─────────────┘  └──────────────────────────────────────────────────┘
```

---

### СТРАНИЦА 12: Bio Links (`/bio-links`)

```
Создание micro-landing pages в стиле Linktree:

- Список созданных bio-страниц
- Конструктор: drag & drop ссылок
- Выбор темы для bio-страницы
- Превью в реальном времени (мобильный фрейм)
- Публичный URL: gosha.link/bio/username

┌──────────────────────┐     ┌──────────────────────┐
│ EDITOR               │     │ PREVIEW (phone frame)│
│                      │     │ ┌──────────────────┐ │
│ Title: [Alex K.]     │     │ │                  │ │
│ Bio:   [Developer]   │     │ │   [Avatar]       │ │
│ Avatar: [Upload]     │     │ │   Alex K.        │ │
│ Theme: [Modern ▾]    │     │ │   Developer      │ │
│                      │     │ │                  │ │
│ Links:               │     │ │ ┌──────────────┐ │ │
│ ⠿ Portfolio     [✏️🗑]│     │ │ │  Portfolio   │ │ │
│ ⠿ GitHub        [✏️🗑]│     │ │ └──────────────┘ │ │
│ ⠿ Twitter       [✏️🗑]│     │ │ ┌──────────────┐ │ │
│ ⠿ Blog          [✏️🗑]│     │ │ │  GitHub      │ │ │
│                      │     │ │ └──────────────┘ │ │
│ [+ Add Link]         │     │ │ ┌──────────────┐ │ │
│                      │     │ │ │  Twitter     │ │ │
│ [Save] [Publish]     │     │ │ └──────────────┘ │ │
│                      │     │ └──────────────────┘ │
└──────────────────────┘     └──────────────────────┘
```

---

### СТРАНИЦА 13: Settings (`/settings`)

```
Tab-навигация внутри страницы:

[General] [Security] [Appearance] [Notifications] [API]

General:
  - Username, Email (readonly), Avatar upload

Security:
  - Change password (old + new + confirm)
  - Active sessions list (с кнопкой "Revoke")
  - Two-factor auth toggle

Appearance:
  - Theme: [☀️ Light] [🌙 Dark] [🖥 System]
  - Language: [English ▾]
  - Default link expiration: [Never ▾]

Notifications:
  - Email when link reaches X clicks
  - Weekly analytics digest

API:
  - API Key display (masked)
  - [Regenerate Key]
  - Usage stats
```

---

### СТРАНИЦА 14: Profile (`/profile`)

```
┌─ SIDEBAR ──┐  ┌──────────────────────────────────────────────────┐
│             │  │                                                  │
│             │  │  ┌──────┐  Alex Kowalski                        │
│             │  │  │Avatar│  @alexk                                │
│             │  │  │      │  alex@example.com                     │
│             │  │  └──────┘  Member since Dec 2024                │
│             │  │            Plan: Free                            │
│             │  │                                                  │
│             │  │  ─────────────────────────────────────────────── │
│             │  │                                                  │
│             │  │  Your Stats:                                     │
│             │  │                                                  │
│             │  │  ┌──────────┐ ┌──────────┐ ┌──────────┐        │
│             │  │  │   47     │ │  1,234   │ │   12     │        │
│             │  │  │ Links    │ │ Total    │ │ QR Codes │        │
│             │  │  │ Created  │ │ Clicks   │ │          │        │
│             │  │  └──────────┘ └──────────┘ └──────────┘        │
│             │  │                                                  │
│             │  │  ┌──────────┐ ┌──────────┐ ┌──────────┐        │
│             │  │  │   3      │ │   89%    │ │   2      │        │
│             │  │  │ Bio      │ │ Links    │ │ Expired  │        │
│             │  │  │ Pages    │ │ Active   │ │ Links    │        │
│             │  │  └──────────┘ └──────────┘ └──────────┘        │
│             │  │                                                  │
│             │  │  Activity heatmap (как на GitHub):               │
│             │  │  ┌──────────────────────────────────────────┐   │
│             │  │  │ Mon ░░░█░░██░░░░█░░░░░░░█░███░░░░░░█░░  │   │
│             │  │  │ Tue ░░░░░░░█░░░░░░░██░░░░░░░░░░███░░░░  │   │
│             │  │  │ Wed ░░█░░░░░░░░█░░░░░░██████░░░░░░░░░░  │   │
│             │  │  │ Thu ░░░░██░░░░░░░░░░░░░░░░░░█████░░░░░  │   │
│             │  │  │ Fri ░█░░░░░░░████░░░░░░░░░░░░░░░░░░░░░  │   │
│             │  │  └──────────────────────────────────────────┘   │
│             │  │                                                  │
│             │  │  Top performing links:                           │
│             │  │  1. gosha.link/my-blog — 456 clicks              │
│             │  │  2. gosha.link/resume — 234 clicks               │
│             │  │  3. gosha.link/portfolio — 189 clicks             │
│             │  │                                                  │
└─────────────┘  └──────────────────────────────────────────────────┘
```

---

### СТРАНИЦА 15: Admin Panel (`/admin`)

```
┌─ SIDEBAR ──┐  ┌──────────────────────────────────────────────────┐
│             │  │                                                  │
│ 🛡️ Admin    │  │  Admin Dashboard                                │
│ ──────────  │  │                                                  │
│ 📊 Overview │  │  Platform Stats:                                 │
│ 👥 Users    │  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────┐ │
│ 🔗 Links    │  │  │  1,247   │ │  45,678  │ │ 234,567  │ │ 89 │ │
│ 📈 Stats    │  │  │ Total    │ │ Total    │ │ Total    │ │ QR │ │
│ ⚙️  Config  │  │  │ Users    │ │ Links    │ │ Clicks   │ │    │ │
│             │  │  └──────────┘ └──────────┘ └──────────┘ └────┘ │
│             │  │                                                  │
│             │  │  Recent registrations:                           │
│             │  │  ┌───────────────────────────────────────────┐  │
│             │  │  │ User │ Email │ Registered │ Links │ Status│  │
│             │  │  │──────│───────│────────────│───────│───────│  │
│             │  │  │ john │ j@... │ 2h ago     │ 3     │ ✅    │  │
│             │  │  │ anna │ a@... │ 5h ago     │ 0     │ ✅    │  │
│             │  │  │ spam │ s@... │ 1d ago     │ 150   │ ⛔    │  │
│             │  │  └───────────────────────────────────────────┘  │
│             │  │                                                  │
│             │  │  Charts: signups/day, links/day, clicks/day     │
│             │  │                                                  │
└─────────────┘  └──────────────────────────────────────────────────┘
```

### Admin Users (`/admin/users`)

```
Таблица всех пользователей:
- Search, filter by role, sort by date/links/clicks
- Actions: [View] [Edit Role] [Ban] [Delete]
- Inline role switch: User ↔ Admin
- Bulk actions
```

### Admin Links (`/admin/links`)

```
Все ссылки на платформе:
- Search по short_code, original_url, username
- Filter: active/disabled/expired
- Actions: [Disable] [Delete] [View Stats]
```

---

## 7. Компоненты дизайна — CSS

### `base.css`

```css
/* ============================================
   RESET & TYPOGRAPHY
   ============================================ */
*, *::before, *::after {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

html {
    scroll-behavior: smooth;
    font-size: 16px;
}

body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    background: var(--bg-primary);
    color: var(--text-primary);
    line-height: 1.6;
    min-height: 100vh;
    transition: background-color 0.4s ease, color 0.3s ease;
}

a {
    color: var(--accent);
    text-decoration: none;
    transition: color var(--transition-fast);
}

a:hover {
    color: var(--accent-hover);
}


/* ============================================
   LAYOUT
   ============================================ */
.page-wrapper {
    display: flex;
    min-height: 100vh;
}

.main-content {
    flex: 1;
    margin-left: var(--sidebar-width);
    padding: 32px;
    padding-top: calc(var(--navbar-height) + 32px);
}

/* На публичных страницах без sidebar */
.main-content--full {
    margin-left: 0;
}

@media (max-width: 768px) {
    .main-content {
        margin-left: 0;
        padding: 16px;
        padding-top: calc(var(--navbar-height) + 16px);
    }
}
```

### `components.css` — переиспользуемые компоненты

```css
/* ============================================
   NAVBAR — sticky, glass effect
   ============================================ */
.navbar {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    z-index: 100;
    height: var(--navbar-height);
    background: var(--navbar-bg);
    backdrop-filter: var(--navbar-blur);
    -webkit-backdrop-filter: var(--navbar-blur);
    border-bottom: 1px solid var(--navbar-border);
    display: flex;
    align-items: center;
    padding: 0 32px;
    transition: background-color 0.3s, border-color 0.3s;
}

.navbar__logo {
    font-size: 22px;
    font-weight: 700;
    color: var(--text-primary);
    display: flex;
    align-items: center;
    gap: 8px;
}

.navbar__logo-icon {
    width: 32px;
    height: 32px;
    background: var(--accent);
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 18px;
}

.navbar__nav {
    display: flex;
    gap: 4px;
    margin-left: 48px;
}

.navbar__link {
    padding: 8px 16px;
    border-radius: var(--radius-sm);
    color: var(--text-muted);
    font-size: 14px;
    font-weight: 500;
    transition: all var(--transition-fast);
}

.navbar__link:hover {
    color: var(--text-primary);
    background: var(--bg-surface-hover);
}

.navbar__link--active {
    color: var(--accent);
    background: var(--accent-light);
}

.navbar__actions {
    margin-left: auto;
    display: flex;
    align-items: center;
    gap: 12px;
}

/* Mobile hamburger */
.navbar__hamburger {
    display: none;
    width: 40px;
    height: 40px;
    border: none;
    background: transparent;
    cursor: pointer;
    position: relative;
}

@media (max-width: 768px) {
    .navbar__nav { display: none; }
    .navbar__nav.open {
        display: flex;
        flex-direction: column;
        position: absolute;
        top: var(--navbar-height);
        left: 0;
        right: 0;
        background: var(--bg-surface);
        border-bottom: 1px solid var(--border-default);
        padding: 16px;
        animation: slideDown 0.3s ease;
    }
    .navbar__hamburger { display: flex; }
}

@keyframes slideDown {
    from { opacity: 0; transform: translateY(-8px); }
    to   { opacity: 1; transform: translateY(0); }
}


/* ============================================
   SIDEBAR — dashboard navigation
   ============================================ */
.sidebar {
    position: fixed;
    top: var(--navbar-height);
    left: 0;
    bottom: 0;
    width: var(--sidebar-width);
    background: var(--sidebar-bg);
    border-right: 1px solid var(--sidebar-border);
    padding: 24px 12px;
    overflow-y: auto;
    z-index: 50;
    transition: transform 0.3s ease, background-color 0.3s;
}

.sidebar__section {
    margin-bottom: 8px;
}

.sidebar__label {
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    color: var(--text-muted);
    padding: 8px 12px;
}

.sidebar__link {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 12px;
    border-radius: var(--radius-sm);
    color: var(--text-muted);
    font-size: 14px;
    font-weight: 500;
    transition: all var(--transition-fast);
}

.sidebar__link:hover {
    color: var(--text-primary);
    background: var(--bg-surface-hover);
}

.sidebar__link--active {
    color: var(--accent);
    background: var(--accent-light);
    font-weight: 600;
}

.sidebar__link-icon {
    font-size: 18px;
    width: 24px;
    text-align: center;
}

.sidebar__divider {
    height: 1px;
    background: var(--border-default);
    margin: 16px 12px;
}

/* Mobile sidebar — выезжает как drawer */
@media (max-width: 768px) {
    .sidebar {
        transform: translateX(-100%);
    }
    .sidebar.open {
        transform: translateX(0);
    }
    .sidebar__overlay {
        position: fixed;
        inset: 0;
        background: rgba(0,0,0,0.4);
        z-index: 49;
        opacity: 0;
        pointer-events: none;
        transition: opacity 0.3s;
    }
    .sidebar.open ~ .sidebar__overlay {
        opacity: 1;
        pointer-events: auto;
    }
}


/* ============================================
   BUTTONS
   ============================================ */

/* Primary Button — оранжевый акцент */
.btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    padding: 12px 24px;
    border: none;
    border-radius: var(--radius-sm);
    font-family: inherit;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: all var(--transition-normal);
    position: relative;
    overflow: hidden;
}

.btn--primary {
    background: var(--accent);
    color: var(--accent-text);
    box-shadow: 0 2px 8px rgba(238, 97, 35, 0.25);
}

.btn--primary:hover {
    background: var(--accent-hover);
    transform: translateY(-1px);
    box-shadow: 0 4px 16px rgba(238, 97, 35, 0.3);
}

.btn--primary:active {
    transform: translateY(0) scale(0.98);
}

/* Shimmer на primary */
.btn--primary::after {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(
        90deg,
        transparent, rgba(255,255,255,0.2), transparent
    );
    transition: left 0.5s;
}

.btn--primary:hover::after {
    left: 100%;
}

/* Secondary Button */
.btn--secondary {
    background: transparent;
    color: var(--text-primary);
    border: 1px solid var(--border-default);
}

.btn--secondary:hover {
    border-color: var(--border-hover);
    background: var(--bg-surface-hover);
}

/* Ghost Button */
.btn--ghost {
    background: transparent;
    color: var(--accent);
}

.btn--ghost:hover {
    background: var(--accent-light);
}

/* Large Button */
.btn--lg {
    padding: 16px 32px;
    font-size: 16px;
    border-radius: var(--radius-md);
}

/* Icon Button */
.btn--icon {
    width: 40px;
    height: 40px;
    padding: 0;
    border-radius: var(--radius-sm);
}


/* ============================================
   CARDS
   ============================================ */
.card {
    background: var(--bg-surface);
    border: 1px solid var(--border-default);
    border-radius: var(--radius-lg);
    padding: 24px;
    transition: all var(--transition-normal);
}

.card:hover {
    box-shadow: var(--shadow-md);
}

.card--elevated {
    box-shadow: var(--shadow-md);
}

.card--elevated:hover {
    box-shadow: var(--shadow-lg);
    transform: translateY(-2px);
}

/* Metric Card — с градиентным фоном */
.metric-card {
    border-radius: var(--radius-lg);
    padding: 24px;
    color: white;
    position: relative;
    overflow: hidden;
}

.metric-card--1 { background: var(--gradient-1); }
.metric-card--2 { background: var(--gradient-2); }
.metric-card--3 { background: var(--gradient-3); }
.metric-card--4 { background: var(--gradient-4); }

.metric-card__value {
    font-size: 36px;
    font-weight: 700;
    line-height: 1;
}

.metric-card__label {
    font-size: 13px;
    opacity: 0.85;
    margin-top: 8px;
}

.metric-card__trend {
    font-size: 12px;
    margin-top: 4px;
    display: flex;
    align-items: center;
    gap: 4px;
}

/* Декоративные круги на metric card */
.metric-card::before {
    content: '';
    position: absolute;
    width: 120px;
    height: 120px;
    background: rgba(255,255,255,0.1);
    border-radius: 50%;
    top: -30px;
    right: -30px;
}

.metric-card::after {
    content: '';
    position: absolute;
    width: 80px;
    height: 80px;
    background: rgba(255,255,255,0.08);
    border-radius: 50%;
    bottom: -20px;
    right: 30px;
}


/* ============================================
   INPUT FIELDS
   ============================================ */
.input {
    width: 100%;
    padding: 12px 16px;
    background: var(--bg-surface);
    border: 1.5px solid var(--border-default);
    border-radius: var(--radius-sm);
    color: var(--text-primary);
    font-family: inherit;
    font-size: 14px;
    outline: none;
    transition: all var(--transition-normal);
}

.input::placeholder {
    color: var(--text-muted);
}

.input:hover {
    border-color: var(--border-hover);
}

.input:focus {
    border-color: var(--accent);
    box-shadow: 0 0 0 3px rgba(238, 97, 35, 0.12);
}

.input--with-icon {
    padding-left: 44px;
}

.input-wrapper {
    position: relative;
}

.input-wrapper__icon {
    position: absolute;
    left: 14px;
    top: 50%;
    transform: translateY(-50%);
    color: var(--text-muted);
    pointer-events: none;
    transition: color var(--transition-fast);
}

.input-wrapper:focus-within .input-wrapper__icon {
    color: var(--accent);
}

.input-label {
    display: block;
    font-size: 13px;
    font-weight: 600;
    color: var(--text-secondary);
    margin-bottom: 6px;
}


/* ============================================
   THEME TOGGLE — красивый переключатель
   ============================================ */
.theme-toggle {
    width: 52px;
    height: 28px;
    border-radius: 14px;
    background: var(--border-default);
    border: none;
    cursor: pointer;
    position: relative;
    transition: background var(--transition-normal);
}

.theme-toggle::before {
    content: '☀️';
    position: absolute;
    width: 22px;
    height: 22px;
    border-radius: 50%;
    background: white;
    top: 3px;
    left: 3px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    transition: all 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
    box-shadow: 0 1px 3px rgba(0,0,0,0.15);
}

[data-theme="dark"] .theme-toggle {
    background: var(--accent);
}

[data-theme="dark"] .theme-toggle::before {
    content: '🌙';
    left: 27px;
}


/* ============================================
   AVATAR DROPDOWN
   ============================================ */
.avatar-menu {
    position: relative;
}

.avatar-btn {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    border: 2px solid var(--border-default);
    cursor: pointer;
    overflow: hidden;
    transition: border-color var(--transition-fast);
}

.avatar-btn:hover {
    border-color: var(--accent);
}

.avatar-btn img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.avatar-dropdown {
    position: absolute;
    top: calc(100% + 8px);
    right: 0;
    width: 220px;
    background: var(--bg-surface);
    border: 1px solid var(--border-default);
    border-radius: var(--radius-md);
    box-shadow: var(--shadow-lg);
    padding: 8px;
    opacity: 0;
    visibility: hidden;
    transform: translateY(-8px) scale(0.95);
    transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
    z-index: 200;
}

.avatar-menu:hover .avatar-dropdown,
.avatar-dropdown.open {
    opacity: 1;
    visibility: visible;
    transform: translateY(0) scale(1);
}

.avatar-dropdown__item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 12px;
    border-radius: var(--radius-xs);
    color: var(--text-primary);
    font-size: 14px;
    transition: background var(--transition-fast);
}

.avatar-dropdown__item:hover {
    background: var(--bg-surface-hover);
}

.avatar-dropdown__item--danger {
    color: var(--error);
}


/* ============================================
   LINK CARD — для списка ссылок
   ============================================ */
.link-card {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 16px 20px;
    background: var(--bg-surface);
    border: 1px solid var(--border-default);
    border-radius: var(--radius-md);
    transition: all var(--transition-normal);
}

.link-card:hover {
    border-color: var(--accent);
    box-shadow: var(--shadow-sm);
}

.link-card__icon {
    width: 40px;
    height: 40px;
    border-radius: var(--radius-sm);
    background: var(--accent-light);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    flex-shrink: 0;
}

.link-card__info {
    flex: 1;
    min-width: 0;
}

.link-card__short {
    font-weight: 600;
    font-size: 15px;
    color: var(--accent);
}

.link-card__original {
    font-size: 13px;
    color: var(--text-muted);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.link-card__meta {
    font-size: 12px;
    color: var(--text-muted);
    margin-top: 4px;
    display: flex;
    gap: 12px;
}

.link-card__stats {
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 14px;
    font-weight: 600;
    color: var(--text-secondary);
}

.link-card__actions {
    display: flex;
    gap: 4px;
}


/* ============================================
   COUNTER ANIMATION — для лендинга
   ============================================ */
.counter {
    font-size: 48px;
    font-weight: 700;
    color: var(--text-primary);
    line-height: 1;
    font-variant-numeric: tabular-nums;
}

.counter__label {
    font-size: 14px;
    color: var(--text-muted);
    font-weight: 400;
    margin-top: 8px;
}


/* ============================================
   CAROUSEL — горизонтальный скролл
   ============================================ */
.carousel {
    position: relative;
    overflow: hidden;
}

.carousel__track {
    display: flex;
    gap: 24px;
    overflow-x: auto;
    scroll-snap-type: x mandatory;
    scroll-behavior: smooth;
    scrollbar-width: none;
    padding: 8px 0;
}

.carousel__track::-webkit-scrollbar {
    display: none;
}

.carousel__item {
    flex: 0 0 340px;
    scroll-snap-align: start;
}

.carousel__btn {
    position: absolute;
    top: 50%;
    transform: translateY(-50%);
    width: 48px;
    height: 48px;
    border-radius: 50%;
    background: var(--bg-surface);
    border: 1px solid var(--border-default);
    box-shadow: var(--shadow-md);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    color: var(--text-primary);
    z-index: 10;
    transition: all var(--transition-normal);
}

.carousel__btn:hover {
    background: var(--accent);
    color: white;
    border-color: var(--accent);
    transform: translateY(-50%) scale(1.05);
}

.carousel__btn--prev { left: 0; }
.carousel__btn--next { right: 0; }


/* ============================================
   TOAST NOTIFICATIONS
   ============================================ */
.toast-container {
    position: fixed;
    top: calc(var(--navbar-height) + 16px);
    right: 16px;
    z-index: 1000;
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.toast {
    min-width: 300px;
    padding: 14px 20px;
    border-radius: var(--radius-md);
    background: var(--bg-surface);
    border: 1px solid var(--border-default);
    box-shadow: var(--shadow-lg);
    display: flex;
    align-items: center;
    gap: 12px;
    animation: toastIn 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}

.toast--success { border-left: 4px solid var(--success); }
.toast--error   { border-left: 4px solid var(--error); }
.toast--warning { border-left: 4px solid var(--warning); }
.toast--info    { border-left: 4px solid var(--info); }

.toast--exit {
    animation: toastOut 0.3s ease forwards;
}

@keyframes toastIn {
    from { opacity: 0; transform: translateX(100px); }
    to   { opacity: 1; transform: translateX(0); }
}

@keyframes toastOut {
    to { opacity: 0; transform: translateX(100px); height: 0; padding: 0; margin: 0; }
}


/* ============================================
   MODAL
   ============================================ */
.modal-overlay {
    position: fixed;
    inset: 0;
    background: rgba(3, 31, 57, 0.5);
    backdrop-filter: blur(4px);
    z-index: 500;
    display: flex;
    align-items: center;
    justify-content: center;
    opacity: 0;
    visibility: hidden;
    transition: all 0.3s ease;
}

.modal-overlay.open {
    opacity: 1;
    visibility: visible;
}

.modal {
    background: var(--bg-surface);
    border-radius: var(--radius-xl);
    padding: 32px;
    max-width: 520px;
    width: 90%;
    max-height: 85vh;
    overflow-y: auto;
    box-shadow: var(--shadow-xl);
    transform: translateY(20px) scale(0.95);
    transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}

.modal-overlay.open .modal {
    transform: translateY(0) scale(1);
}

.modal__header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 24px;
}

.modal__title {
    font-size: 20px;
    font-weight: 700;
}

.modal__close {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    border: none;
    background: var(--bg-surface-hover);
    cursor: pointer;
    font-size: 18px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all var(--transition-fast);
}

.modal__close:hover {
    background: var(--error-light);
    color: var(--error);
}


/* ============================================
   TABLE — для админки
   ============================================ */
.table-wrapper {
    overflow-x: auto;
    border: 1px solid var(--border-default);
    border-radius: var(--radius-md);
}

.table {
    width: 100%;
    border-collapse: collapse;
}

.table th {
    text-align: left;
    padding: 12px 16px;
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: var(--text-muted);
    background: var(--bg-secondary);
    border-bottom: 1px solid var(--border-default);
}

.table td {
    padding: 12px 16px;
    font-size: 14px;
    border-bottom: 1px solid var(--border-default);
}

.table tr:last-child td {
    border-bottom: none;
}

.table tr:hover td {
    background: var(--bg-surface-hover);
}

/* Status badges */
.badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 4px 10px;
    border-radius: var(--radius-full);
    font-size: 12px;
    font-weight: 600;
}

.badge--success {
    background: var(--success-light);
    color: var(--success);
}

.badge--error {
    background: var(--error-light);
    color: var(--error);
}

.badge--warning {
    background: var(--warning-light);
    color: var(--warning);
}

.badge--info {
    background: var(--info-light);
    color: var(--info);
}


/* ============================================
   PAGINATION
   ============================================ */
.pagination {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 4px;
    margin-top: 24px;
}

.pagination__btn {
    width: 36px;
    height: 36px;
    border-radius: var(--radius-sm);
    border: 1px solid var(--border-default);
    background: var(--bg-surface);
    cursor: pointer;
    font-size: 14px;
    color: var(--text-primary);
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all var(--transition-fast);
}

.pagination__btn:hover {
    border-color: var(--accent);
    color: var(--accent);
}

.pagination__btn--active {
    background: var(--accent);
    color: white;
    border-color: var(--accent);
}


/* ============================================
   SECTION ANIMATIONS — Intersection Observer
   ============================================ */
.animate-on-scroll {
    opacity: 0;
    transform: translateY(30px);
    transition: all 0.8s cubic-bezier(0.16, 1, 0.3, 1);
}

.animate-on-scroll.visible {
    opacity: 1;
    transform: translateY(0);
}

/* Stagger children */
.stagger-children .animate-on-scroll:nth-child(1) { transition-delay: 0s; }
.stagger-children .animate-on-scroll:nth-child(2) { transition-delay: 0.1s; }
.stagger-children .animate-on-scroll:nth-child(3) { transition-delay: 0.2s; }
.stagger-children .animate-on-scroll:nth-child(4) { transition-delay: 0.3s; }


/* ============================================
   PASSWORD STRENGTH INDICATOR
   ============================================ */
.password-strength {
    height: 4px;
    border-radius: 2px;
    background: var(--border-default);
    margin-top: 8px;
    overflow: hidden;
}

.password-strength__bar {
    height: 100%;
    border-radius: 2px;
    transition: width 0.4s ease, background 0.4s ease;
}

.password-strength__bar--weak   { width: 25%; background: var(--error); }
.password-strength__bar--fair   { width: 50%; background: var(--warning); }
.password-strength__bar--good   { width: 75%; background: var(--info); }
.password-strength__bar--strong { width: 100%; background: var(--success); }
```

---

## 8. JavaScript — ключевые модули

### `theme.js` — переключение тем

```javascript
/**
 * Theme Manager
 * 
 * Сохраняет выбор в localStorage + отправляет на сервер
 * для синхронизации с БД (user.theme_preference).
 */
class ThemeManager {
    constructor() {
        this.currentTheme = this.getSavedTheme();
        this.apply(this.currentTheme);
        this.bindToggle();
    }

    getSavedTheme() {
        // Приоритет: localStorage → системная тема
        const saved = localStorage.getItem('theme');
        if (saved) return saved;

        return window.matchMedia('(prefers-color-scheme: dark)').matches
            ? 'dark'
            : 'light';
    }

    apply(theme) {
        // Включаем transition перед сменой
        document.documentElement.setAttribute('data-theme-transition', '');

        document.documentElement.setAttribute('data-theme', theme);
        this.currentTheme = theme;
        localStorage.setItem('theme', theme);

        // Убираем transition через 500ms чтобы не тормозило обычные взаимодействия
        setTimeout(() => {
            document.documentElement.removeAttribute('data-theme-transition');
        }, 500);
    }

    toggle() {
        const next = this.currentTheme === 'light' ? 'dark' : 'light';
        this.apply(next);

        // Синхронизируем с сервером (если залогинен)
        this.syncWithServer(next);
    }

    async syncWithServer(theme) {
        try {
            await fetch('/api/v1/users/me/theme', {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ theme }),
            });
        } catch (e) {
            // Не критично — localStorage уже сохранён
        }
    }

    bindToggle() {
        document.querySelectorAll('.theme-toggle').forEach(btn => {
            btn.addEventListener('click', () => this.toggle());
        });
    }
}

// Инициализация при загрузке (до рендера, чтобы избежать мерцания)
const themeManager = new ThemeManager();
```

### `app.js` — общая логика

```javascript
/**
 * Toast Notification System
 */
class Toast {
    static container = null;

    static init() {
        this.container = document.createElement('div');
        this.container.className = 'toast-container';
        document.body.appendChild(this.container);
    }

    static show(message, type = 'info', duration = 4000) {
        if (!this.container) this.init();

        const icons = {
            success: '✅', error: '❌', warning: '⚠️', info: 'ℹ️'
        };

        const toast = document.createElement('div');
        toast.className = `toast toast--${type}`;
        toast.innerHTML = `
            <span>${icons[type]}</span>
            <span>${message}</span>
        `;

        this.container.appendChild(toast);

        // Авто-скрытие
        setTimeout(() => {
            toast.classList.add('toast--exit');
            toast.addEventListener('animationend', () => toast.remove());
        }, duration);
    }
}


/**
 * Counter Animation — числа "набегают"
 */
class CounterAnimation {
    static observe() {
        const counters = document.querySelectorAll('[data-counter]');
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    this.animate(entry.target);
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.5 });

        counters.forEach(el => observer.observe(el));
    }

    static animate(element) {
        const target = parseInt(element.dataset.counter);
        const suffix = element.dataset.suffix || '';
        const duration = 2000;
        const startTime = performance.now();

        const update = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            // easeOutExpo для плавного замедления в конце
            const eased = 1 - Math.pow(2, -10 * progress);
            const current = Math.floor(eased * target);

            element.textContent = current.toLocaleString() + suffix;

            if (progress < 1) {
                requestAnimationFrame(update);
            }
        };

        requestAnimationFrame(update);
    }
}


/**
 * Scroll Animations — Intersection Observer
 */
class ScrollAnimations {
    static init() {
        const elements = document.querySelectorAll('.animate-on-scroll');
        const observer = new IntersectionObserver(
            (entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('visible');
                    }
                });
            },
            { threshold: 0.1, rootMargin: '0px 0px -50px 0px' }
        );

        elements.forEach(el => observer.observe(el));
    }
}


/**
 * API Helper — обёртка для fetch с JWT refresh
 */
class API {
    static async request(url, options = {}) {
        const defaults = {
            headers: { 'Content-Type': 'application/json' },
        };

        let response = await fetch(url, { ...defaults, ...options });

        // Если 401 — пробуем refresh
        if (response.status === 401) {
            const refreshed = await this.refreshToken();
            if (refreshed) {
                response = await fetch(url, { ...defaults, ...options });
            } else {
                window.location.href = '/login';
                return null;
            }
        }

        return response;
    }

    static async refreshToken() {
        try {
            const res = await fetch('/api/v1/auth/refresh', { method: 'POST' });
            return res.ok;
        } catch {
            return false;
        }
    }
}


// Инициализация при загрузке
document.addEventListener('DOMContentLoaded', () => {
    CounterAnimation.observe();
    ScrollAnimations.init();
});
```

### `carousel.js` — карусель на лендинге

```javascript
class Carousel {
    constructor(element) {
        this.track = element.querySelector('.carousel__track');
        this.prevBtn = element.querySelector('.carousel__btn--prev');
        this.nextBtn = element.querySelector('.carousel__btn--next');
        this.itemWidth = 340 + 24; // width + gap

        this.prevBtn?.addEventListener('click', () => this.scroll(-1));
        this.nextBtn?.addEventListener('click', () => this.scroll(1));

        // Touch swipe support
        this.bindTouch();
    }

    scroll(direction) {
        const amount = this.itemWidth * direction;
        this.track.scrollBy({ left: amount, behavior: 'smooth' });
    }

    bindTouch() {
        let startX = 0;
        this.track.addEventListener('touchstart', (e) => {
            startX = e.touches[0].clientX;
        }, { passive: true });

        this.track.addEventListener('touchend', (e) => {
            const diff = startX - e.changedTouches[0].clientX;
            if (Math.abs(diff) > 50) {
                this.scroll(diff > 0 ? 1 : -1);
            }
        }, { passive: true });
    }
}

// Инициализация всех каруселей
document.querySelectorAll('.carousel').forEach(el => new Carousel(el));
```

---

## 9. Шаблоны Jinja2

### `base.html` — базовый layout

```html
<!DOCTYPE html>
<html lang="ru" data-theme="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Gosha{% endblock %} — Connections Platform</title>

    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">

    <link rel="stylesheet" href="/static/css/variables.css">
    <link rel="stylesheet" href="/static/css/base.css">
    <link rel="stylesheet" href="/static/css/components.css">
    {% block extra_css %}{% endblock %}

    <!-- Инициализация темы ДО рендера (предотвращает мерцание) -->
    <script>
        const saved = localStorage.getItem('theme');
        if (saved) document.documentElement.setAttribute('data-theme', saved);
        else if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
            document.documentElement.setAttribute('data-theme', 'dark');
        }
    </script>
</head>
<body>

    {% block navbar %}
        {% if current_user %}
            {% include "components/navbar_auth.html" %}
        {% else %}
            {% include "components/navbar_public.html" %}
        {% endif %}
    {% endblock %}

    {% block sidebar %}{% endblock %}

    <main class="main-content {% block main_class %}{% endblock %}">
        {% block content %}{% endblock %}
    </main>

    {% block footer %}
        {% include "components/footer.html" %}
    {% endblock %}

    <script src="/static/js/theme.js"></script>
    <script src="/static/js/app.js"></script>
    {% block extra_js %}{% endblock %}

</body>
</html>
```

### `components/navbar_public.html`

```html
<nav class="navbar">
    <a href="/" class="navbar__logo">
        <div class="navbar__logo-icon">G</div>
        Gosha
    </a>

    <div class="navbar__nav" id="navMenu">
        <a href="/features" class="navbar__link
            {% if active_page == 'features' %}navbar__link--active{% endif %}">
            Features
        </a>
        <a href="/pricing" class="navbar__link
            {% if active_page == 'pricing' %}navbar__link--active{% endif %}">
            Pricing
        </a>
        <a href="/about" class="navbar__link
            {% if active_page == 'about' %}navbar__link--active{% endif %}">
            About
        </a>
    </div>

    <div class="navbar__actions">
        <button class="theme-toggle" aria-label="Toggle theme"></button>
        <a href="/login" class="btn btn--ghost">Log in</a>
        <a href="/register" class="btn btn--primary">Sign up free</a>
    </div>

    <button class="navbar__hamburger" onclick="document.getElementById('navMenu').classList.toggle('open')">
        ☰
    </button>
</nav>
```

### `components/navbar_auth.html`

```html
<nav class="navbar">
    <a href="/dashboard" class="navbar__logo">
        <div class="navbar__logo-icon">G</div>
        Gosha
    </a>

    <div class="navbar__nav" id="navMenu">
        <a href="/dashboard" class="navbar__link
            {% if active_page == 'dashboard' %}navbar__link--active{% endif %}">
            Dashboard
        </a>
        <a href="/links" class="navbar__link
            {% if active_page == 'links' %}navbar__link--active{% endif %}">
            Links
        </a>
        <a href="/analytics" class="navbar__link
            {% if active_page == 'analytics' %}navbar__link--active{% endif %}">
            Analytics
        </a>
        <a href="/qr-codes" class="navbar__link
            {% if active_page == 'qr' %}navbar__link--active{% endif %}">
            QR Codes
        </a>
        <a href="/bio-links" class="navbar__link
            {% if active_page == 'bio' %}navbar__link--active{% endif %}">
            Bio Links
        </a>
    </div>

    <div class="navbar__actions">
        <button class="theme-toggle" aria-label="Toggle theme"></button>

        <div class="avatar-menu">
            <button class="avatar-btn">
                {% if current_user.avatar_url %}
                    <img src="{{ current_user.avatar_url }}" alt="Avatar">
                {% else %}
                    <div style="display:flex;align-items:center;justify-content:center;
                                width:100%;height:100%;background:var(--accent);
                                color:white;font-weight:700;font-size:14px;">
                        {{ current_user.username[0]|upper }}
                    </div>
                {% endif %}
            </button>

            <div class="avatar-dropdown">
                <div style="padding:12px;border-bottom:1px solid var(--border-default);margin-bottom:4px;">
                    <div style="font-weight:600;">{{ current_user.username }}</div>
                    <div style="font-size:12px;color:var(--text-muted);">{{ current_user.email }}</div>
                </div>
                <a href="/profile" class="avatar-dropdown__item">👤 Profile</a>
                <a href="/settings" class="avatar-dropdown__item">⚙️ Settings</a>
                {% if current_user.is_admin %}
                    <a href="/admin" class="avatar-dropdown__item">🛡️ Admin Panel</a>
                {% endif %}
                <div style="height:1px;background:var(--border-default);margin:4px 0;"></div>
                <a href="#" class="avatar-dropdown__item avatar-dropdown__item--danger"
                   onclick="logout()">🚪 Log out</a>
            </div>
        </div>
    </div>
</nav>
```

### `components/footer.html`

```html
<footer style="
    background: var(--bg-secondary);
    border-top: 1px solid var(--border-default);
    padding: 64px 32px 32px;
    margin-top: 80px;
    transition: background 0.3s, border-color 0.3s;
">
    <div style="max-width: 1200px; margin: 0 auto;">

        <!-- Верхняя часть: 4 колонки -->
        <div style="display:grid; grid-template-columns: 2fr 1fr 1fr 1fr; gap:48px; margin-bottom:48px;">

            <!-- Бренд -->
            <div>
                <div style="font-size:24px;font-weight:700;margin-bottom:12px;display:flex;align-items:center;gap:8px;">
                    <div style="width:32px;height:32px;background:var(--accent);border-radius:8px;
                                display:flex;align-items:center;justify-content:center;color:white;">G</div>
                    Gosha
                </div>
                <p style="color:var(--text-muted);font-size:14px;line-height:1.6;max-width:280px;">
                    Build stronger digital connections with our URL shortener,
                    QR Codes, and Bio Links platform.
                </p>
            </div>

            <!-- Products -->
            <div>
                <h4 style="font-size:13px;font-weight:600;text-transform:uppercase;
                           letter-spacing:1px;color:var(--text-muted);margin-bottom:16px;">
                    Products
                </h4>
                <div style="display:flex;flex-direction:column;gap:10px;">
                    <a href="/features" style="color:var(--text-secondary);font-size:14px;">URL Shortener</a>
                    <a href="/features" style="color:var(--text-secondary);font-size:14px;">QR Codes</a>
                    <a href="/features" style="color:var(--text-secondary);font-size:14px;">Bio Links</a>
                    <a href="/features" style="color:var(--text-secondary);font-size:14px;">Analytics</a>
                </div>
            </div>

            <!-- Company -->
            <div>
                <h4 style="font-size:13px;font-weight:600;text-transform:uppercase;
                           letter-spacing:1px;color:var(--text-muted);margin-bottom:16px;">
                    Company
                </h4>
                <div style="display:flex;flex-direction:column;gap:10px;">
                    <a href="/about" style="color:var(--text-secondary);font-size:14px;">About</a>
                    <a href="/pricing" style="color:var(--text-secondary);font-size:14px;">Pricing</a>
                    <a href="#" style="color:var(--text-secondary);font-size:14px;">Blog</a>
                    <a href="#" style="color:var(--text-secondary);font-size:14px;">Contact</a>
                </div>
            </div>

            <!-- Legal -->
            <div>
                <h4 style="font-size:13px;font-weight:600;text-transform:uppercase;
                           letter-spacing:1px;color:var(--text-muted);margin-bottom:16px;">
                    Legal
                </h4>
                <div style="display:flex;flex-direction:column;gap:10px;">
                    <a href="#" style="color:var(--text-secondary);font-size:14px;">Privacy Policy</a>
                    <a href="#" style="color:var(--text-secondary);font-size:14px;">Terms of Service</a>
                    <a href="#" style="color:var(--text-secondary);font-size:14px;">Cookie Policy</a>
                </div>
            </div>
        </div>

        <!-- Нижняя часть -->
        <div style="border-top:1px solid var(--border-default);padding-top:24px;
                    display:flex;justify-content:space-between;align-items:center;
                    flex-wrap:wrap;gap:12px;">
            <span style="color:var(--text-muted);font-size:13px;">
                © 2024 Gosha Connections Platform
            </span>
            <a href="https://github.com/ternopolskiy"
               target="_blank"
               rel="noopener noreferrer"
               style="color:var(--text-muted);font-size:13px;display:flex;align-items:center;gap:6px;
                      transition:color 0.3s;">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                    <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47
                    7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37
                    -2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68
                    -.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87
                    2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64
                    -3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12
                    0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09
                    2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08
                    2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65
                    3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01
                    2.14 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42
                    -3.58-8-8-8z"/>
                </svg>
                Made by ternopolskiy
            </a>
        </div>
    </div>
</footer>
```

---

## 10. Полная карта API эндпоинтов

```
AUTH:
  POST   /api/v1/auth/register         — регистрация
  POST   /api/v1/auth/login            — вход
  POST   /api/v1/auth/logout           — выход
  POST   /api/v1/auth/refresh          — обновить access token
  GET    /api/v1/auth/me               — текущий пользователь

LINKS:
  POST   /api/v1/links                 — создать короткую ссылку
  GET    /api/v1/links                 — мои ссылки (pagination, search)
  GET    /api/v1/links/{id}            — детали ссылки
  PATCH  /api/v1/links/{id}            — обновить (title, tags, active)
  DELETE /api/v1/links/{id}            — удалить
  POST   /api/v1/links/bulk-delete     — удалить несколько

ANALYTICS:
  GET    /api/v1/analytics/overview    — общая статистика
  GET    /api/v1/analytics/link/{id}   — статистика по ссылке
  GET    /api/v1/analytics/clicks      — клики за период
  GET    /api/v1/analytics/referrers   — топ рефереры
  GET    /api/v1/analytics/devices     — устройства
  GET    /api/v1/analytics/countries   — страны
  GET    /api/v1/analytics/export      — экспорт CSV

QR CODES:
  POST   /api/v1/qr                    — создать QR код
  GET    /api/v1/qr                    — мои QR коды
  GET    /api/v1/qr/{id}              — получить QR
  DELETE /api/v1/qr/{id}              — удалить QR

BIO LINKS:
  POST   /api/v1/bio                   — создать bio-страницу
  GET    /api/v1/bio                   — мои bio-страницы
  GET    /api/v1/bio/{id}             — детали
  PATCH  /api/v1/bio/{id}             — обновить
  DELETE /api/v1/bio/{id}             — удалить
  POST   /api/v1/bio/{id}/links       — добавить ссылку
  PATCH  /api/v1/bio/{id}/links/{lid} — обновить ссылку
  DELETE /api/v1/bio/{id}/links/{lid} — удалить ссылку
  PATCH  /api/v1/bio/{id}/reorder     — изменить порядок

USERS:
  GET    /api/v1/users/me              — мой профиль
  PATCH  /api/v1/users/me              — обновить профиль
  PATCH  /api/v1/users/me/password     — сменить пароль
  PATCH  /api/v1/users/me/theme        — сменить тему
  DELETE /api/v1/users/me              — удалить аккаунт

ADMIN (require_admin):
  GET    /api/v1/admin/stats           — статистика платформы
  GET    /api/v1/admin/users           — все пользователи
  GET    /api/v1/admin/users/{id}      — детали пользователя
  PATCH  /api/v1/admin/users/{id}      — обновить (role, active)
  DELETE /api/v1/admin/users/{id}      — удалить пользователя
  GET    /api/v1/admin/links           — все ссылки
  DELETE /api/v1/admin/links/{id}      — удалить ссылку

REDIRECT (публичный):
  GET    /{short_code}                 — редирект
  GET    /bio/{slug}                   — публичная bio-страница
```

---

## 11. Page Routes — роутинг для HTML страниц

```python
# app/pages/public.py

from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from app.core.dependencies import get_current_user_optional

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/")
async def landing(request: Request, user=Depends(get_current_user_optional)):
    # Если залогинен — редирект на dashboard
    if user:
        return RedirectResponse("/dashboard")

    return templates.TemplateResponse("public/landing.html", {
        "request": request,
        "active_page": "home",
    })


@router.get("/features")
async def features(request: Request, user=Depends(get_current_user_optional)):
    return templates.TemplateResponse("public/features.html", {
        "request": request,
        "current_user": user,
        "active_page": "features",
    })


@router.get("/pricing")
async def pricing(request: Request, user=Depends(get_current_user_optional)):
    return templates.TemplateResponse("public/pricing.html", {
        "request": request,
        "current_user": user,
        "active_page": "pricing",
    })


@router.get("/about")
async def about(request: Request, user=Depends(get_current_user_optional)):
    return templates.TemplateResponse("public/about.html", {
        "request": request,
        "current_user": user,
        "active_page": "about",
    })
```

```python
# app/pages/auth_pages.py

from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from app.core.dependencies import get_current_user_optional

router = APIRouter()


@router.get("/login")
async def login_page(request: Request, user=Depends(get_current_user_optional)):
    if user:
        return RedirectResponse("/dashboard")
    return templates.TemplateResponse("auth/login.html", {
        "request": request,
        "active_page": "login",
    })


@router.get("/register")
async def register_page(request: Request, user=Depends(get_current_user_optional)):
    if user:
        return RedirectResponse("/dashboard")
    return templates.TemplateResponse("auth/register.html", {
        "request": request,
        "active_page": "register",
    })
```

```python
# app/pages/dashboard.py

from fastapi import APIRouter, Request, Depends
from app.core.dependencies import get_current_user

router = APIRouter()


@router.get("/dashboard")
async def dashboard(request: Request, user=Depends(get_current_user)):
    return templates.TemplateResponse("dashboard/index.html", {
        "request": request,
        "current_user": user,
        "active_page": "dashboard",
    })


@router.get("/links")
async def links_page(request: Request, user=Depends(get_current_user)):
    return templates.TemplateResponse("dashboard/links.html", {
        "request": request,
        "current_user": user,
        "active_page": "links",
    })


@router.get("/analytics")
async def analytics_page(request: Request, user=Depends(get_current_user)):
    return templates.TemplateResponse("dashboard/analytics.html", {
        "request": request,
        "current_user": user,
        "active_page": "analytics",
    })

# ... аналогично для /qr-codes, /bio-links, /settings, /profile
```

```python
# app/pages/admin_pages.py

from fastapi import APIRouter, Request, Depends
from app.core.dependencies import require_admin

router = APIRouter(prefix="/admin")


@router.get("")
async def admin_dashboard(request: Request, user=Depends(require_admin)):
    return templates.TemplateResponse("admin/index.html", {
        "request": request,
        "current_user": user,
        "active_page": "admin",
    })


@router.get("/users")
async def admin_users(request: Request, user=Depends(require_admin)):
    return templates.TemplateResponse("admin/users.html", {
        "request": request,
        "current_user": user,
        "active_page": "admin_users",
    })

# ... /admin/links, /admin/stats
```

---

## 12. `main.py` — собираем всё вместе

```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.api import auth, links, analytics, users, qr, bio, admin
from app.pages import public, auth_pages, dashboard, admin_pages

# Создаём таблицы
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Gosha Connections Platform",
    version="2.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# ===== API Routes (порядок важен!) =====
app.include_router(auth.router)
app.include_router(links.router)
app.include_router(analytics.router)
app.include_router(users.router)
app.include_router(qr.router)
app.include_router(bio.router)
app.include_router(admin.router)

# ===== Page Routes =====
app.include_router(public.router)
app.include_router(auth_pages.router)
app.include_router(dashboard.router)
app.include_router(admin_pages.router)

# ===== Redirect (ПОСЛЕДНИЙ — catch-all) =====
from app.api.redirect import router as redirect_router
app.include_router(redirect_router)


@app.get("/api/health")
async def health():
    return {"status": "ok", "version": "2.0.0"}
```

---

## 13. Config

```python
# app/config.py

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./gosha.db"

    # JWT
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # App
    BASE_URL: str = "http://localhost:8000"
    SHORT_CODE_LENGTH: int = 6

    # Admin (создаётся при первом запуске)
    ADMIN_EMAIL: str = "admin@gosha.link"
    ADMIN_PASSWORD: str = "Admin123!"
    ADMIN_USERNAME: str = "admin"

    class Config:
        env_file = ".env"


settings = Settings()
```

---

## 14. `requirements.txt`

```
fastapi==0.115.0
uvicorn==0.30.0
sqlalchemy==2.0.35
pydantic[email]==2.9.0
pydantic-settings==2.5.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
httpx==0.27.0
jinja2==3.1.4
python-multipart==0.0.9
qrcode[pil]==7.4.2
user-agents==2.2.0
pytest==8.3.0
pytest-cov==5.0.0
```

---

## 15. Итоговая карта всего сайта

```
PUBLIC (без авторизации):
┌────────────────────────────────────────────────────────────┐
│  /             Landing page (маркетинг, CTA)              │
│  /features     Описание фич (4 секции)                    │
│  /pricing      Тарифы (3 плана + FAQ)                     │
│  /about        О компании, команда, миссия                │
│  /login        Форма входа                                │
│  /register     Форма регистрации + сила пароля            │
│  /{code}       Редирект по короткой ссылке                │
│  /bio/{slug}   Публичная bio-страница                     │
└────────────────────────────────────────────────────────────┘

USER (после входа):
┌────────────────────────────────────────────────────────────┐
│  /dashboard    Метрики + quick shorten + график + recent  │
│  /links        Все ссылки + поиск + фильтры + bulk ops    │
│  /link/{id}    Детали ссылки + графики + устройства       │
│  /analytics    Общая аналитика + экспорт CSV              │
│  /qr-codes     QR коды + конструктор стилей               │
│  /bio-links    Bio страницы + drag & drop конструктор     │
│  /settings     4 таба: General/Security/Appearance/API    │
│  /profile      Профиль + статистика + activity heatmap    │
└────────────────────────────────────────────────────────────┘

ADMIN (role=admin):
┌────────────────────────────────────────────────────────────┐
│  /admin        Дашборд платформы + метрики + графики      │
│  /admin/users  Таблица пользователей + actions            │
│  /admin/links  Все ссылки на платформе + модерация        │
│  /admin/stats  Детальная статистика + графики роста        │
└────────────────────────────────────────────────────────────┘

Итого: 18 уникальных страниц
       42 API эндпоинта
       2 роли (user, admin)
       Светлая + тёмная тема
       Полная мобильная адаптация
```