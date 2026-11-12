from app.core.config import settings
from app.integrations.ai.base import AIProvider
from app.integrations.ai.exceptions import AIConfigurationError
from app.integrations.ai.providers.mock_provider import MockAIProvider


def create_ai_provider() -> AIProvider:
    """
    Create the provider selected by application settings.
    """

    if settings.ai_provider == "mock":
        return MockAIProvider()

    if settings.ai_provider == "gemini":
        if not settings.gemini_api_key:
            raise AIConfigurationError(
                "GEMINI_API_KEY is required when "
                "AI_PROVIDER=gemini."
            )

        from app.integrations.ai.providers.gemini_provider import (
            GeminiProvider,
        )

        return GeminiProvider(
            api_key=settings.gemini_api_key,
            model=settings.gemini_model,
            temperature=settings.ai_temperature,
            max_output_tokens=settings.ai_max_output_tokens,
            timeout_seconds=settings.ai_timeout_seconds,
        )

    raise AIConfigurationError(
        f"Unsupported AI provider: {settings.ai_provider}"
    )