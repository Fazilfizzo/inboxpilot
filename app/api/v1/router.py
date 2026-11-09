from fastapi import APIRouter

from app.api.v1.endpoints import emails, health
from app.core.config import settings

router = APIRouter()

router.include_router(health.router)
router.include_router(
    emails.router,
    prefix=settings.api_v1_prefix,
)