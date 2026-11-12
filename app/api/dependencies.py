from fastapi import Request

from app.integrations.ai.base import AIProvider


def get_ai_provider(request: Request) -> AIProvider:
    return request.app.state.ai_provider