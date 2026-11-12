from types import SimpleNamespace

import pytest
from pydantic import BaseModel

from app.integrations.ai.exceptions import AIInvalidResponseError
from app.integrations.ai.providers.gemini_provider import GeminiProvider


class ExampleResponse(BaseModel):
    message: str
    success: bool


class FakeAsyncModels:
    def __init__(self, response):
        self.response = response
        self.calls = 0

    async def generate_content(self, **kwargs):
        self.calls += 1
        return self.response


class FakeAsyncClient:
    def __init__(self, models):
        self.models = models
        self.closed = False

    async def aclose(self):
        self.closed = True


class FakeClient:
    def __init__(self, models):
        self.aio = FakeAsyncClient(models)


def create_provider(response):
    fake_models = FakeAsyncModels(response)
    fake_client = FakeClient(fake_models)

    provider = GeminiProvider(
        api_key="test-key",
        model="test-model",
        client=fake_client,
    )

    return provider, fake_models, fake_client


@pytest.mark.asyncio
async def test_returns_validated_parsed_response():
    response = SimpleNamespace(
        parsed={
            "message": "Email classified",
            "success": True,
        },
        text='{"message": "Email classified", "success": true}',
    )

    provider, _, _ = create_provider(response)

    result = await provider.generate_structured(
        prompt="Classify this email",
        response_schema=ExampleResponse,
    )

    assert isinstance(result, ExampleResponse)
    assert result.message == "Email classified"
    assert result.success is True


@pytest.mark.asyncio
async def test_falls_back_to_json_text():
    response = SimpleNamespace(
        parsed=None,
        text='{"message": "Fallback response", "success": true}',
    )

    provider, _, _ = create_provider(response)

    result = await provider.generate_structured(
        prompt="Test",
        response_schema=ExampleResponse,
    )

    assert result.message == "Fallback response"


@pytest.mark.asyncio
async def test_rejects_invalid_json_schema():
    response = SimpleNamespace(
        parsed=None,
        text='{"unexpected": "value"}',
    )

    provider, _, _ = create_provider(response)

    with pytest.raises(AIInvalidResponseError):
        await provider.generate_structured(
            prompt="Test",
            response_schema=ExampleResponse,
        )


@pytest.mark.asyncio
async def test_rejects_empty_prompt():
    response = SimpleNamespace(
        parsed=None,
        text="",
    )

    provider, _, _ = create_provider(response)

    with pytest.raises(ValueError):
        await provider.generate_structured(
            prompt="   ",
            response_schema=ExampleResponse,
        )


@pytest.mark.asyncio
async def test_closes_async_client():
    response = SimpleNamespace(
        parsed=None,
        text="",
    )

    provider, _, fake_client = create_provider(response)

    await provider.aclose()

    assert fake_client.aio.closed is True