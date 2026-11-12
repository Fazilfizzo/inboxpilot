
import base64

import pytest

from app.integrations.gmail.exceptions import (
    GmailMessageParsingError,
)
from app.integrations.gmail.parser import (
    decode_body_data,
    extract_email_body,
    parse_gmail_message,
)


def encode_body(text: str) -> str:
    return base64.urlsafe_b64encode(
        text.encode("utf-8")
    ).decode("utf-8").rstrip("=")


def make_message(
    body: str,
    mime_type: str = "text/plain",
    subject: str = "Payment problem",
) -> dict:
    return {
        "id": "gmail-message-123",
        "threadId": "gmail-thread-456",
        "internalDate": "1790000000000",
        "payload": {
            "mimeType": mime_type,
            "headers": [
                {
                    "name": "From",
                    "value": "John Smith <john@example.com>",
                },
                {
                    "name": "Subject",
                    "value": subject,
                },
                {
                    "name": "Content-Type",
                    "value": f"{mime_type}; charset=UTF-8",
                },
            ],
            "body": {
                "data": encode_body(body),
            },
        },
    }


def test_decode_base64url_body():
    encoded = encode_body("Hello InboxPilot")

    assert decode_body_data(encoded) == "Hello InboxPilot"


def test_parse_plain_text_message():
    message = make_message(
        "I paid yesterday but my order is still pending."
    )

    result = parse_gmail_message(message)

    assert result.gmail_message_id == "gmail-message-123"
    assert result.thread_id == "gmail-thread-456"
    assert result.sender == "john@example.com"
    assert result.subject == "Payment problem"
    assert "order is still pending" in result.body
    assert result.received_at is not None


def test_parse_html_message():
    message = make_message(
        "<html><body><h1>Hello</h1><p>Payment failed.</p>"
        "<script>alert('ignore')</script></body></html>",
        mime_type="text/html",
    )

    result = parse_gmail_message(message)

    assert "Hello" in result.body
    assert "Payment failed." in result.body
    assert "alert" not in result.body


def test_parse_message_without_subject():
    message = make_message(
        "I need help with my order.",
        subject="",
    )

    result = parse_gmail_message(message)

    assert result.subject == "(No subject)"


def test_reject_message_without_readable_body():
    message = {
        "id": "message-123",
        "threadId": "thread-123",
        "payload": {
            "mimeType": "multipart/mixed",
            "headers": [
                {
                    "name": "From",
                    "value": "customer@example.com",
                },
                {
                    "name": "Subject",
                    "value": "Help",
                },
            ],
            "parts": [],
        },
    }

    with pytest.raises(GmailMessageParsingError):
        parse_gmail_message(message)


def test_plain_text_is_preferred_over_html():
    payload = {
        "mimeType": "multipart/alternative",
        "parts": [
            {
                "mimeType": "text/plain",
                "body": {"data": encode_body("Plain version")},
            },
            {
                "mimeType": "text/html",
                "body": {"data": encode_body("<p>HTML version</p>")},
            },
        ],
    }

    result = extract_email_body(payload)

    assert result == "Plain version"
