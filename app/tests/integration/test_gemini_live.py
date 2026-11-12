import os

import pytest
from pydantic import BaseModel, Field

from app.core.config import settings
from app.integrations.ai.providers.gemini_provider import GeminiProvider


class GeminiTestResponse(BaseModel):
    category: str = Field(description="The email category")


@pytest.mark.asyncio
@pytest.mark.skipif(
    os.getenv("RUN_GEMINI_INTEGRATION_TESTS") != "true",
    reason="Live Gemini tests are disabled.",
)
async def test_gemini_generates_structured_response():

    if not settings.gemini_api_key:
        pytest.skip("GEMINI_API_KEY is not configured.")

    provider = GeminiProvider(
        api_key=settings.gemini_api_key,
        model=settings.gemini_model,
        timeout_seconds=settings.ai_timeout_seconds,
    )

    try:
        result = await provider.generate_structured(
            prompt=(
                "Classify this synthetic customer message: "
                "'I cannot log into my account.'"
            ),
            response_schema=GeminiTestResponse,
            system_instruction=(
                "You classify customer emails. "
                "Return only the requested structured result."
            ),
        )

        assert result.category.strip()

    finally:
        await provider.aclose()