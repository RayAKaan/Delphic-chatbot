from typing import Literal

from fastapi import APIRouter

from app.config.settings import get_settings

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check() -> dict[str, str | Literal["ok"]]:
    settings = get_settings()
    return {
        "status": "ok",
        "app": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
    }
