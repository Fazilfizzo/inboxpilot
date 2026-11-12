from typing import Annotated
from fastapi import APIRouter, Depends

from app.api.dependencies import get_ai_classification_service
from app.schemas.classification import ClassificationResponse
from app.schemas.email import EmailRequest
from app.services.ai_classification_service import AIClassificationService
from app.services.classification_service import classify_email

router = APIRouter(
    prefix="/emails",
    tags=["Emails"],
)


@router.post(
    "/classify",
    response_model=ClassificationResponse,
)
def classify_customer_email(
    email: EmailRequest,
) -> ClassificationResponse:
    return classify_email(email)


@router.post(
    "/classify/ai",
    response_model=ClassificationResponse,
)
async def classify_customer_email_with_ai(
    email: EmailRequest,
    service: Annotated[
        AIClassificationService,
        Depends(get_ai_classification_service),
    ],
) -> ClassificationResponse:
    return await service.classify_email(email)
