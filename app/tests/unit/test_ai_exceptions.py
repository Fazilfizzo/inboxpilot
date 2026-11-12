
from app.integrations.ai.exceptions import (
    AIAuthenticationError,
    AIConfigurationError,
    AIProviderError,
    AIProviderUnavailableError,
    AIRateLimitError,
    AIQuotaExceededError,
)


def test_all_exceptions_inherit_from_base():
    assert issubclass(AIAuthenticationError, AIProviderError)
    assert issubclass(AIConfigurationError, AIProviderError)
    assert issubclass(AIRateLimitError, AIProviderError)


def test_exception_stores_metadata():
    error = AIRateLimitError(
        "Rate limit exceeded.",
        provider="gemini",
        status_code=429,
    )

    assert error.provider == "gemini"
    assert error.status_code == 429
    assert error.retryable is True


def test_non_retryable_error():
    error = AIAuthenticationError(
        "Authentication failed.",
        provider="gemini",
        status_code=401,
    )

    assert error.retryable is False


def test_quota_error_is_not_retryable():
    error = AIQuotaExceededError(
        "Quota exhausted.",
        provider="gemini",
        status_code=429,
    )

    assert isinstance(error, AIRateLimitError)
    assert error.retryable is False


def test_retryable_can_be_overridden():
    error = AIProviderUnavailableError(
        "Provider unavailable.",
        retryable=False,
    )

    assert error.retryable is False
