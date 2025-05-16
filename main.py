from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pathlib import Path
from app.config import settings
from app.routers import chat, upload
from app.db import Base, engine

# Crear tablas
Base.metadata.create_all(bind=engine)

app = FastAPI(title="GALA Avanzado")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def ui():
    f = Path(__file__).parent.parent / "templates" / "index.html"
    return HTMLResponse(f.read_text(encoding="utf-8"))

# Routers
app.include_router(chat.router)
app.include_router(upload.router)
