
import re

from app.schemas.email import EmailRequest
from app.schemas.gmail import ParsedGmailEmail


def normalize_subject(subject: str) -> str:
    """Remove unnecessary whitespace from an email subject."""

    return " ".join(subject.split())


def normalize_body(body: str) -> str:
    """Normalize line endings and remove unwanted control characters."""

    body = body.replace("\r\n", "\n").replace("\r", "\n")

    # Remove null bytes and control characters, preserving tabs/newlines.
    body = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", body)

    return body.strip()


def normalize_gmail_email(
    email: ParsedGmailEmail,
) -> EmailRequest:
    """
    Convert a parsed Gmail message into the standard InboxPilot
    email request contract.
    """

    sender = str(email.sender).strip()
    subject = normalize_subject(email.subject)
    body = normalize_body(email.body)

    return EmailRequest(
        sender=sender,
        subject=subject,
        body=body,
    )
