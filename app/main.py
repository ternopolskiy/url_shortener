from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.database import Base, engine
from app.routes import router


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="URL Shortener",
    description="Сервис сокращения ссылок",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(router)

templates = Jinja2Templates(directory="app/templates")


@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.get("/")
async def ui(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
