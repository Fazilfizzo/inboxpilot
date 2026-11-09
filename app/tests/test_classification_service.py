import pytest

from app.schemas.email import EmailRequest
from app.services.classification_service import classify_email
from app.models.enums import (
    EmailCategory,
    EmailPriority,
    EmailSentiment,
)


@pytest.mark.parametrize(
    "subject, body, expected_category",
    [
        (
            "Payment problem",
            "I paid yesterday but my order is pending.",
            EmailCategory.PAYMENT_ISSUE,
        ),
        (
            "Delivery question",
            "Where is my package?",
            EmailCategory.ORDER_STATUS,
        ),
        (
            "Bad experience",
            "Your service is terrible and disappointing.",
            EmailCategory.COMPLAINT,
        ),
        (
            "Product information",
            "Do you have this product in stock?",
            EmailCategory.GENERAL,
        ),
    ],
)
def test_email_category(
    subject,
    body,
    expected_category,
):
    email = EmailRequest(
        sender="customer@example.com",
        subject=subject,
        body=body,
    )

    result = classify_email(email)

    assert result.category == expected_category


def test_high_priority_email():
    email = EmailRequest(
        sender="customer@example.com",
        subject="Urgent payment issue",
        body="I was charged twice. Please help immediately.",
    )

    result = classify_email(email)

    assert result.priority == EmailPriority.HIGH


def test_medium_priority_email():
    email = EmailRequest(
        sender="customer@example.com",
        subject="Delivery problem",
        body="My package is delayed. Can you help?",
    )

    result = classify_email(email)

    assert result.priority == EmailPriority.MEDIUM


def test_low_priority_email():
    email = EmailRequest(
        sender="customer@example.com",
        subject="General information",
        body="I would like to know your opening hours.",
    )

    result = classify_email(email)

    assert result.priority == EmailPriority.LOW


def test_positive_sentiment():
    email = EmailRequest(
        sender="customer@example.com",
        subject="Thank you",
        body="Your service is excellent. I am happy!",
    )

    result = classify_email(email)

    assert result.sentiment == EmailSentiment.POSITIVE


def test_negative_sentiment():
    email = EmailRequest(
        sender="customer@example.com",
        subject="Bad experience",
        body="I am disappointed and unhappy.",
    )

    result = classify_email(email)

    assert result.sentiment == EmailSentiment.NEGATIVE


def test_neutral_sentiment():
    email = EmailRequest(
        sender="customer@example.com",
        subject="Delivery date",
        body="When will my package arrive?",
    )

    result = classify_email(email)

    assert result.sentiment == EmailSentiment.NEUTRAL


def test_payment_issue_requires_human_review():
    email = EmailRequest(
        sender="customer@example.com",
        subject="Payment question",
        body="I paid yesterday.",
    )

    result = classify_email(email)

    assert result.requires_human is True


def test_general_email_does_not_require_human_review():
    email = EmailRequest(
        sender="customer@example.com",
        subject="Opening hours",
        body="What time does your shop open?",
    )

    result = classify_email(email)

    assert result.requires_human is False
