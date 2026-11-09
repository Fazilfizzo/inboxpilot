from app.models.enums import (
    EmailCategory,
    EmailPriority,
    EmailSentiment,
)
from app.schemas.email import EmailRequest
from app.schemas.classification import ClassificationResponse


# --------------------------------------------------
# Classification keywords
# --------------------------------------------------

PAYMENT_KEYWORDS = (
    "payment",
    "paid",
    "charged",
    "refund",
    "transaction",
    "invoice",
    "billing",
    "duplicate charge",
    "charged twice",
)

COMPLAINT_KEYWORDS = (
    "disappointed",
    "terrible",
    "damaged",
    "broken",
    "unacceptable",
    "poor service",
    "angry",
    "frustrated",
    "not satisfied",
)

ORDER_KEYWORDS = (
    "order",
    "delivery",
    "package",
    "shipment",
    "tracking",
    "parcel",
)

HIGH_PRIORITY_KEYWORDS = (
    "urgent",
    "immediately",
    "as soon as possible",
    "charged twice",
    "duplicate charge",
    "unauthorized charge",
    "fraud",
    "account hacked",
)

MEDIUM_PRIORITY_KEYWORDS = (
    "problem",
    "issue",
    "delayed",
    "missing",
    "refund",
    "damaged",
    "broken",
    "help",
)

POSITIVE_KEYWORDS = (
    "excellent",
    "happy",
    "great",
    "thank you",
    "thanks",
    "appreciate",
    "wonderful",
    "satisfied",
)

NEGATIVE_KEYWORDS = (
    "angry",
    "disappointed",
    "terrible",
    "frustrated",
    "unhappy",
    "poor service",
    "not happy",
    "not satisfied",
    "unacceptable",
)


# --------------------------------------------------
# Category detection
# --------------------------------------------------


def detect_category(text: str) -> EmailCategory:
    if any(keyword in text for keyword in PAYMENT_KEYWORDS):
        return EmailCategory.PAYMENT_ISSUE

    if any(keyword in text for keyword in COMPLAINT_KEYWORDS):
        return EmailCategory.COMPLAINT

    if any(keyword in text for keyword in ORDER_KEYWORDS):
        return EmailCategory.ORDER_STATUS

    return EmailCategory.GENERAL


# --------------------------------------------------
# Priority detection
# --------------------------------------------------


def detect_priority(text: str) -> EmailPriority:
    if any(keyword in text for keyword in HIGH_PRIORITY_KEYWORDS):
        return EmailPriority.HIGH

    if any(keyword in text for keyword in MEDIUM_PRIORITY_KEYWORDS):
        return EmailPriority.MEDIUM

    return EmailPriority.LOW


# --------------------------------------------------
# Sentiment detection
# --------------------------------------------------


def detect_sentiment(text: str) -> EmailSentiment:
    positive_score = sum(text.count(keyword) for keyword in POSITIVE_KEYWORDS)

    negative_score = sum(text.count(keyword) for keyword in NEGATIVE_KEYWORDS)

    if positive_score > negative_score:
        return EmailSentiment.POSITIVE

    if negative_score > positive_score:
        return EmailSentiment.NEGATIVE

    return EmailSentiment.NEUTRAL


# --------------------------------------------------
# Human review decision
# --------------------------------------------------


def requires_human_review(
    category: EmailCategory,
    priority: EmailPriority,
    sentiment: EmailSentiment,
) -> bool:

    sensitive_categories = {
        EmailCategory.PAYMENT_ISSUE,
        EmailCategory.COMPLAINT,
    }

    return (
        category in sensitive_categories
        or priority == EmailPriority.HIGH
        or sentiment == EmailSentiment.NEGATIVE
    )


# --------------------------------------------------
# Main classification function
# --------------------------------------------------


def classify_email(
    email: EmailRequest,
) -> ClassificationResponse:

    text = f"{email.subject} {email.body}".casefold()

    category = detect_category(text)
    priority = detect_priority(text)
    sentiment = detect_sentiment(text)

    human_review = requires_human_review(
        category=category,
        priority=priority,
        sentiment=sentiment,
    )

    return ClassificationResponse(
        category=category,
        priority=priority,
        sentiment=sentiment,
        requires_human=human_review,
    )
