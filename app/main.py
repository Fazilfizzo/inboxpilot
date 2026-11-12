from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import router
from app.core.config import settings
from app.integrations.ai.factory import create_ai_provider


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application-wide resources.
    """

    provider = create_ai_provider()
    app.state.ai_provider = provider

    try:
        yield
    finally:
        await provider.aclose()


app = FastAPI(
    title=settings.app_name,
    description=(
        "An intelligent email classification "
        "and response automation system."
    ),
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
)

app.include_router(router)