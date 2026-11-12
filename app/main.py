
from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI

from app.api.router import router
from app.core.config import settings
from app.integrations.ai.factory import create_ai_provider

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application-wide resources.
    """
    logger.info("Starting InboxPilot application.")

    # Application startup
    provider = create_ai_provider()
    app.state.ai_provider = provider

    logger.info("AI provider initialized successfully.")

    try:
        yield

    finally:
        # Application shutdown
        logger.info("Closing AI provider.")

        await provider.aclose()

        logger.info("AI provider closed successfully.")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
)

app.include_router(
    router,
    prefix=settings.api_v1_prefix,
)
