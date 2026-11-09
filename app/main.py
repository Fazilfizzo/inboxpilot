from fastapi import FastAPI

from app.api.router import router
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    description=(
        "An intelligent email classification "
        "and response automation system."
    ),
    version=settings.app_version,
    debug=settings.debug,
)

app.include_router(router)