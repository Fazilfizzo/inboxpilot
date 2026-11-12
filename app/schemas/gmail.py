from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ParsedGmailEmail(BaseModel):
    """Normalized email extracted from a Gmail message."""

    model_config = ConfigDict(extra="forbid")

    gmail_message_id: str = Field(min_length=1)
    thread_id: str = Field(min_length=1)

    sender: EmailStr
    subject: str = Field(min_length=1, max_length=998)
    body: str = Field(min_length=1, max_length=10000)

    received_at: datetime | None = None
