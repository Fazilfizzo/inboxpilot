from pydantic import BaseModel

from app.integrations.ai.base import AIProvider, T


class MockAIProvider(AIProvider):
    def __init__(
        self,
        responses: dict[type[BaseModel], BaseModel] | None = None,
    ) -> None:
        self.responses = responses or {}

    async def generate_structured(
        self,
        prompt: str,
        response_schema: type[T],
        system_instruction: str | None = None,
    ) -> T:

        response = self.responses.get(response_schema)

        if response is None:
            raise ValueError(
                f"No mock response configured for "
                f"{response_schema.__name__}"
            )

        return response_schema.model_validate(
            response.model_dump()
        )

    async def aclose(self) -> None:
        """No external resources need to be closed."""
        return None