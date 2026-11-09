from fastapi import APIRouter

from app.schemas.classification import ClassificationResponse
from app.schemas.email import EmailRequest
from app.services.classification_service import classify_email

router = APIRouter(
    prefix="/emails",
    tags=["Emails"],
)


@router.post(
    "/classify",
    response_model=ClassificationResponse,
)
def classify_customer_email(email: EmailRequest):
    return classify_email(email)
