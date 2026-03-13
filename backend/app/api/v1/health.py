from fastapi import APIRouter
from app.core.config import settings

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/")
async def health():
    return {"status": "ok", "version": settings.VERSION, "app": settings.APP_NAME}
