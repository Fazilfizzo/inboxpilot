from abc import ABC, abstractmethod
from typing import TypeVar

from pydantic import BaseModel


T = TypeVar("T", bound=BaseModel)


class AIProvider(ABC):
    """
    Common contract for all AI providers.

    Application services should depend on this
    abstraction instead of a specific AI SDK.
    """

    @abstractmethod
    async def generate_structured(
        self,
        prompt: str,
        response_schema: type[T],
        system_instruction: str | None = None,
    ) -> T:
        """
        Generate a structured response validated
        against a Pydantic model.
        """
        raise NotImplementedError

    @abstractmethod
    async def aclose(self) -> None:
        """Release provider resources."""
        raise NotImplementedError