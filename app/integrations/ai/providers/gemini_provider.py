import asyncio
import logging
from typing import Any

from google import genai
from google.genai import errors, types
from pydantic import BaseModel, ValidationError
from tenacity import (
    AsyncRetrying,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)

from app.integrations.ai.base import AIProvider, T
from app.integrations.ai.exceptions import (
    AIAuthenticationError,
    AIInvalidResponseError,
    AIProviderError,
    AIProviderUnavailableError,
    AIRateLimitError,
    AITimeoutError,
)

logger = logging.getLogger(__name__)


def is_retryable_error(exception: BaseException) -> bool:
    """
    Return True only for temporary failures.

    Authentication errors and invalid requests
    should not be retried.
    """

    if isinstance(exception, errors.APIError):
        status_code = getattr(exception, "code", None)

        return (
            status_code == 429
            or (
                isinstance(status_code, int)
                and status_code >= 500
            )
        )

    return isinstance(
        exception,
        (TimeoutError, ConnectionError, OSError),
    )


class GeminiProvider(AIProvider):
    def __init__(
        self,
        api_key: str,
        model: str,
        temperature: float = 0.2,
        max_output_tokens: int = 1000,
        timeout_seconds: int = 30,
        client: Any | None = None,
    ) -> None:
        if not api_key:
            raise ValueError("Gemini API key is required.")

        if not model:
            raise ValueError("Gemini model is required.")

        if not 0 <= temperature <= 2:
            raise ValueError("Temperature must be between 0 and 2.")

        if max_output_tokens < 1:
            raise ValueError("Maximum output tokens must be positive.")

        if timeout_seconds < 1:
            raise ValueError("Timeout must be positive.")

        self.model = model
        self.temperature = temperature
        self.max_output_tokens = max_output_tokens
        self.timeout_seconds = timeout_seconds

        self._client = client or genai.Client(api_key=api_key)
        self._async_client = self._client.aio

    async def _request(
        self,
        prompt: str,
        response_schema: type[BaseModel],
        system_instruction: str | None,
    ):
        """
        Execute one Gemini API request.

        This method is wrapped by the retry policy.
        """

        config = types.GenerateContentConfig(
            temperature=self.temperature,
            max_output_tokens=self.max_output_tokens,
            response_mime_type="application/json",
            response_schema=response_schema,
            system_instruction=system_instruction,
        )

        return await asyncio.wait_for(
            self._async_client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=config,
            ),
            timeout=self.timeout_seconds,
        )

    async def _generate_with_retry(
        self,
        prompt: str,
        response_schema: type[BaseModel],
        system_instruction: str | None,
    ):
        """
        Retry temporary failures up to three attempts.

        Exponential delays: approximately 1s, 2s.
        """

        async for attempt in AsyncRetrying(
            retry=retry_if_exception(is_retryable_error),
            wait=wait_exponential(
                multiplier=1,
                min=1,
                max=8,
            ),
            stop=stop_after_attempt(3),
            reraise=True,
        ):
            with attempt:
                return await self._request(
                    prompt=prompt,
                    response_schema=response_schema,
                    system_instruction=system_instruction,
                )

        raise AIProviderError("Gemini request failed.")

    async def generate_structured(
        self,
        prompt: str,
        response_schema: type[T],
        system_instruction: str | None = None,
    ) -> T:

        if not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        try:
            response = await self._generate_with_retry(
                prompt=prompt,
                response_schema=response_schema,
                system_instruction=system_instruction,
            )

        except errors.APIError as exc:
            status_code = getattr(exc, "code", None)

            # Do not log the request, API key or customer content.
            logger.warning(
                "Gemini API error. status_code=%s",
                status_code,
            )

            if status_code in (401, 403):
                raise AIAuthenticationError(
                    "Gemini authentication failed.",
                    provider="gemini",
                    status_code=status_code,
                ) from exc

            if status_code == 429:
                raise AIRateLimitError(
                    "Gemini rate limit or quota exceeded.",
                    provider="gemini",
                    status_code=status_code,
                ) from exc

            if (
                isinstance(status_code, int)
                and status_code >= 500
            ):
                raise AIProviderUnavailableError(
                    "Gemini is temporarily unavailable."
                ) from exc

            raise AIProviderError(
                "Gemini request was rejected."
            ) from exc

        except TimeoutError as exc:
            raise AITimeoutError(
                "Gemini request timed out."
            ) from exc

        except (ConnectionError, OSError) as exc:
            raise AIProviderUnavailableError(
                "Could not connect to Gemini."
            ) from exc

        except Exception as exc:
            logger.exception("Unexpected Gemini integration failure.")

            raise AIProviderError(
                "Unexpected Gemini integration failure."
            ) from exc

        if not response.text and response.parsed is None:
            raise AIInvalidResponseError(
                "Gemini returned an empty response."
            )

        try:
            if response.parsed is not None:
                return response_schema.model_validate(
                    response.parsed
                )

            return response_schema.model_validate_json(
                response.text
            )

        except (ValidationError, ValueError, TypeError) as exc:
            logger.warning(
                "Gemini returned an invalid structured response."
            )

            raise AIInvalidResponseError(
                "Gemini response failed Pydantic validation."
            ) from exc

    async def aclose(self) -> None:
        """Close the asynchronous Gemini client."""

        await self._async_client.aclose()