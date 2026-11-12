
import pytest
from pydantic import ValidationError

from app.schemas.gmail import ParsedGmailEmail
from app.services.email_normalization_service import (
    normalize_body,
    normalize_gmail_email,
    normalize_subject,
)


def make_parsed_email(
    sender: str = "customer@example.com",
    subject: str = "Payment problem",
    body: str = "My payment is still pending.",
) -> ParsedGmailEmail:
    return ParsedGmailEmail(
        gmail_message_id="message-123",
        thread_id="thread-123",
        sender=sender,
        subject=subject,
        body=body,
    )


def test_normalize_subject():
    result = normalize_subject("   Payment    problem   ")

    assert result == "Payment problem"


def test_normalize_body():
    result = normalize_body(
        "  Hello\r\nWorld\x00\tTest  "
    )

    assert result == "Hello\nWorld\tTest"


def test_normalize_gmail_email():
    parsed_email = make_parsed_email(
        subject="  Payment    problem ",
        body="  I paid yesterday.\r\n My order is pending.  ",
    )

    result = normalize_gmail_email(parsed_email)

    assert result.sender == "customer@example.com"
    assert result.subject == "Payment problem"
    assert result.body == (
        "I paid yesterday.\n My order is pending."
    )


def test_reject_subject_exceeding_maximum_length():
    parsed_email = make_parsed_email(
        subject="A" * 201,
    )

    with pytest.raises(ValidationError):
        normalize_gmail_email(parsed_email)


def test_reject_body_shorter_than_minimum_length():
    parsed_email = make_parsed_email(body="Hi")

    with pytest.raises(ValidationError):
        normalize_gmail_email(parsed_email)


def test_reject_empty_normalized_body():
    parsed_email = make_parsed_email(body="   \n   ")

    with pytest.raises(ValidationError):
        normalize_gmail_email(parsed_email)
