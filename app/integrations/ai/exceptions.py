
class AIProviderError(Exception):
    """
    Base exception for all AI provider integration errors.

    All provider-specific exceptions should inherit from this class.
    """

    default_retryable = False

    def __init__(
        self,
        message: str,
        *,
        provider: str | None = None,
        status_code: int | None = None,
        retryable: bool | None = None,
    ) -> None:
        super().__init__(message)

        self.provider = provider
        self.status_code = status_code
        self.retryable = (
            self.default_retryable
            if retryable is None
            else retryable
        )


class AIConfigurationError(AIProviderError):
    """Missing or invalid AI provider configuration."""


class AIAuthenticationError(AIProviderError):
    """AI provider authentication failed."""


class AIRateLimitError(AIProviderError):
    """AI provider request rate limit was exceeded."""

    default_retryable = True


class AIQuotaExceededError(AIRateLimitError):
    """AI provider usage quota has been exhausted."""

    default_retryable = False


class AIProviderUnavailableError(AIProviderError):
    """AI provider is temporarily unavailable."""

    default_retryable = True


class AITimeoutError(AIProviderError):
    """AI provider request exceeded the configured timeout."""

    default_retryable = True


class AIInvalidResponseError(AIProviderError):
    """AI provider returned an empty or invalid response."""


class AIRequestError(AIProviderError):
    """AI provider rejected a request because of invalid parameters."""
