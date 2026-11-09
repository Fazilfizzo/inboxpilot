from enum import Enum


class EmailCategory(str, Enum):
    PAYMENT_ISSUE = "payment_issue"
    ORDER_STATUS = "order_status"
    COMPLAINT = "complaint"
    GENERAL = "general"


class EmailPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class EmailSentiment(str, Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


class EmailStatus(str, Enum):
    NEW = "new"
    CLASSIFIED = "classified"
    AWAITING_APPROVAL = "awaiting_approval"
    APPROVED = "approved"
    SENT = "sent"
    FAILED = "failed"
