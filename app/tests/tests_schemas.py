import pytest
from pydantic import ValidationError

from app.schemas.email import EmailRequest
from app.schemas.classification import ClassificationResponse


def test_valid_email_request():
    email = EmailRequest(
        sender="customer@gmail.com",
        subject="Payment problem",
        body="I paid yesterday but my order is pending.",
    )

    assert email.sender == "customer@gmail.com"
    assert email.subject == "Payment problem"


def test_invalid_email_address():
    with pytest.raises(ValidationError):
        EmailRequest(
            sender="invalid-email", subject="Payment problem", body="I paid yesterday."
        )


def test_subject_too_short():
    with pytest.raises(ValidationError):
        EmailRequest(
            sender="customer@gmail.com", subject="A", body="I need help with my order."
        )


def test_invalid_classification_category():
    with pytest.raises(ValidationError):
        ClassificationResponse(
            category="unknown_category",
            priority="high",
            sentiment="negative",
            requires_human=True,
        )


def test_valid_classification_response():
    result = ClassificationResponse(
        category="payment_issue",
        priority="high",
        sentiment="negative",
        requires_human=True,
    )

    assert result.category.value == "payment_issue"
