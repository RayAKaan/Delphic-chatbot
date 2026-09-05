import logging

from fastapi import FastAPI

from app.api.conversations import router as conversations_router
from app.api.health import router as health_router
from app.config.settings import get_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()

app = FastAPI(title=settings.app_name, version=settings.app_version)

app.include_router(health_router)
app.include_router(conversations_router)


@app.get("/")
def root() -> dict[str, str]:
    return {"app": settings.app_name, "docs": "/docs", "health": "/health"}
