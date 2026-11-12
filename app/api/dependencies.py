
from fastapi import Depends, Request

from app.integrations.ai.base import AIProvider
from app.services.ai_classification_service import AIClassificationService


def get_ai_provider(request: Request) -> AIProvider:
    """Retrieve the shared AI provider from application state."""
    provider = getattr(request.app.state, "ai_provider", None)

    if provider is None:
        raise RuntimeError("AI provider has not been initialized.")

    return provider


def get_ai_classification_service(
    provider: AIProvider = Depends(get_ai_provider),
) -> AIClassificationService:
    """Create an AI classification service using the shared provider."""
    return AIClassificationService(provider=provider)
