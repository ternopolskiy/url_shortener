from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.api import admin, analytics, auth, links, redirect, users, qr
from app.config import settings
from app.core.dependencies import get_current_user, require_admin, get_current_user_optional
from app.database import Base, engine, get_db
from app.models import User
from app.migrations import run_all_migrations

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
app.include_router(users.router)
app.include_router(analytics.router)
app.include_router(admin.router)
app.include_router(qr.router)

# ===== Page Routes =====


@app.get("/")
async def landing(request: Request, db: Session = Depends(get_db)):
    """Landing page - redirects to dashboard if authenticated."""
    # Check if user is authenticated
    try:
        token = request.cookies.get("access_token")
        if token:
            from app.core.security import decode_token
            
            payload = decode_token(token)
            if payload and payload.get("type") == "access":
                user_id = payload.get("sub")
                user = db.query(User).filter(User.id == int(user_id)).first()
                
                if user and user.is_active:
                    # User is authenticated - redirect to dashboard
                    return RedirectResponse(url="/dashboard", status_code=302)
    except:
        pass  # Not authenticated, show landing page
    
    return templates.TemplateResponse(
        "landing.html", {"request": request, "active_page": "home"}
    )


@app.get("/features")
async def features_page(request: Request):
    """Features page."""
    return templates.TemplateResponse(
        "public/features.html", {"request": request, "active_page": "features"}
    )


@app.get("/pricing")
async def pricing_page(request: Request):
    """Pricing page."""
    return templates.TemplateResponse(
        "public/pricing.html", {"request": request, "active_page": "pricing"}
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


@app.get("/qr-codes")
async def qr_codes_page(
    request: Request, current_user: User = Depends(get_current_user)
):
    """QR Codes page (requires authentication)."""
    return templates.TemplateResponse(
        "dashboard/qr_codes.html",
        {
            "request": request,
            "current_user": current_user,
            "active_page": "qr-codes",
        },
    )


@app.get("/profile")
async def profile_page(
    request: Request, current_user: User = Depends(get_current_user)
):
    """Profile page (requires authentication)."""
    return templates.TemplateResponse(
        "dashboard/profile.html",
        {
            "request": request,
            "current_user": current_user,
            "active_page": "profile",
        },
    )


@app.get("/settings")
async def settings_page(
    request: Request, current_user: User = Depends(get_current_user)
):
    """Settings page (requires authentication)."""
    return templates.TemplateResponse(
        "dashboard/settings.html",
        {
            "request": request,
            "current_user": current_user,
            "active_page": "settings",
        },
    )


@app.get("/admin")
async def admin_page(
    request: Request, current_user: User = Depends(require_admin)
):
    """Admin panel (requires admin role)."""
    return templates.TemplateResponse(
        "admin/index.html",
        {
            "request": request,
            "current_user": current_user,
            "active_page": "admin",
        },
    )


@app.get("/login")
async def login_page(request: Request, db: Session = Depends(get_db)):
    """Login page - redirects to dashboard if already authenticated."""
    # Check if user is authenticated
    try:
        token = request.cookies.get("access_token")
        if token:
            from app.core.security import decode_token
            
            payload = decode_token(token)
            if payload and payload.get("type") == "access":
                user_id = payload.get("sub")
                user = db.query(User).filter(User.id == int(user_id)).first()
                
                if user and user.is_active:
                    return RedirectResponse(url="/dashboard", status_code=302)
    except:
        pass
    
    return templates.TemplateResponse(
        "auth/login.html", {"request": request, "active_page": "login"}
    )


@app.get("/register")
async def register_page(request: Request, db: Session = Depends(get_db)):
    """Register page - redirects to dashboard if already authenticated."""
    # Check if user is authenticated
    try:
        token = request.cookies.get("access_token")
        if token:
            from app.core.security import decode_token
            
            payload = decode_token(token)
            if payload and payload.get("type") == "access":
                user_id = payload.get("sub")
                user = db.query(User).filter(User.id == int(user_id)).first()
                
                if user and user.is_active:
                    return RedirectResponse(url="/dashboard", status_code=302)
    except:
        pass
    
    return templates.TemplateResponse(
        "auth/register.html", {"request": request, "active_page": "register"}
    )


@app.get("/forgot-password")
async def forgot_password_page(request: Request):
    """Forgot password page."""
    return templates.TemplateResponse(
        "auth/forgot_password.html", {"request": request, "active_page": "forgot-password"}
    )


# ===== Redirect (LAST - catch-all) =====
app.include_router(redirect.router)


@app.get("/api/health")
async def health():
    return {"status": "ok", "version": "2.0.0"}


# Create admin user on startup if not exists
@app.on_event("startup")
async def startup_migrations():
    # Run database migrations
    run_all_migrations()
    
    # Create admin user
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
