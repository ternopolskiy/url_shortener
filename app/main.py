from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api import auth, links, redirect
from app.config import settings
from app.core.dependencies import get_current_user, get_current_user_optional
from app.database import Base, engine
from app.models import User

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Gosha Connections Platform",
    description="URL Shortener, QR Codes, and Bio Links Platform",
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

# Templates
templates = Jinja2Templates(directory="app/templates")

# ===== API Routes =====
app.include_router(auth.router)
app.include_router(links.router)

# ===== Page Routes =====


@app.get("/")
async def landing(request: Request):
    """Landing page."""
    return templates.TemplateResponse(
        "landing.html", {"request": request, "active_page": "home"}
    )


@app.get("/dashboard")
async def dashboard(
    request: Request, current_user: User = Depends(get_current_user)
):
    """Dashboard page (requires authentication)."""
    return templates.TemplateResponse(
        "dashboard/index.html",
        {
            "request": request,
            "current_user": current_user,
            "active_page": "dashboard",
        },
    )


@app.get("/links")
async def links_page(
    request: Request, current_user: User = Depends(get_current_user)
):
    """Links page (requires authentication)."""
    return templates.TemplateResponse(
        "dashboard/links.html",
        {
            "request": request,
            "current_user": current_user,
            "active_page": "links",
        },
    )


@app.get("/analytics")
async def analytics_page(
    request: Request, current_user: User = Depends(get_current_user)
):
    """Analytics page (requires authentication)."""
    return templates.TemplateResponse(
        "dashboard/analytics.html",
        {
            "request": request,
            "current_user": current_user,
            "active_page": "analytics",
        },
    )


@app.get("/login")
async def login_page(request: Request):
    """Login page."""
    return templates.TemplateResponse(
        "auth/login.html", {"request": request, "active_page": "login"}
    )


@app.get("/register")
async def register_page(request: Request):
    """Register page."""
    return templates.TemplateResponse(
        "auth/register.html", {"request": request, "active_page": "register"}
    )


# ===== Redirect (LAST - catch-all) =====
app.include_router(redirect.router)


@app.get("/api/health")
async def health():
    return {"status": "ok", "version": "2.0.0"}


# Create admin user on startup if not exists
@app.on_event("startup")
async def create_admin():
    from app.core.security import hash_password
    from app.database import SessionLocal
    from app.models import User, UserRole

    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.role == UserRole.ADMIN).first()
        if not admin:
            admin = User(
                email=settings.ADMIN_EMAIL,
                username=settings.ADMIN_USERNAME,
                hashed_password=hash_password(settings.ADMIN_PASSWORD),
                role=UserRole.ADMIN,
                is_active=True,
            )
            db.add(admin)
            db.commit()
            print(f"✅ Admin user created: {settings.ADMIN_EMAIL}")
    finally:
        db.close()
