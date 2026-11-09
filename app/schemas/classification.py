from pydantic import BaseModel

from app.models.enums import (
    EmailCategory,
    EmailPriority,
    EmailSentiment,
)


class ClassificationResponse(BaseModel):
    category: EmailCategory
    priority: EmailPriority
    sentiment: EmailSentiment
    requires_human: bool
