from fastapi import APIRouter, Depends

from app.api.dependencies import get_ai_provider
from app.integrations.ai.base import AIProvider

router = APIRouter()


@router.get("/ai-status")
async def ai_status(
    provider: AIProvider = Depends(get_ai_provider),
):
    return {
        "provider": provider.__class__.__name__,
        "status": "configured",
    }