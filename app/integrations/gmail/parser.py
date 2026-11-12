
import base64
import logging
import re
from datetime import datetime, timezone
from email.header import decode_header, make_header
from email.utils import parseaddr
from html.parser import HTMLParser
from typing import Any

from pydantic import EmailStr, TypeAdapter, ValidationError

from app.integrations.gmail.exceptions import (
    GmailMessageParsingError,
)
from app.schemas.gmail  import ParsedGmailEmail

logger = logging.getLogger(__name__)


class HTMLTextExtractor(HTMLParser):
    """Extract readable text from HTML while ignoring scripts and styles."""

    IGNORED_TAGS = {"script", "style", "head"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.text_parts: list[str] = []
        self.ignored_depth = 0

    def handle_starttag(self, tag: str, attrs: list) -> None:
        if tag in self.IGNORED_TAGS:
            self.ignored_depth += 1

        elif tag in {"br", "p", "div", "li", "tr"}:
            if self.ignored_depth == 0:
                self.text_parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in self.IGNORED_TAGS and self.ignored_depth > 0:
            self.ignored_depth -= 1

        elif tag in {"p", "div", "li", "tr"}:
            if self.ignored_depth == 0:
                self.text_parts.append("\n")

    def handle_data(self, data: str) -> None:
        if self.ignored_depth == 0:
            self.text_parts.append(data)

    def get_text(self) -> str:
        return clean_body(" ".join(self.text_parts))


def clean_body(body: str) -> str:
    """Normalize whitespace without removing meaningful paragraph breaks."""

    body = body.replace("\r\n", "\n").replace("\r", "\n")
    body = re.sub(r"[ \t]+", " ", body)
    body = re.sub(r" *\n *", "\n", body)
    body = re.sub(r"\n{3,}", "\n\n", body)

    return body.strip()


def decode_header_value(value: str | None) -> str:
    """Decode an RFC 2047 encoded email header."""

    if not value:
        return ""

    try:
        return str(make_header(decode_header(value))).strip()
    except (ValueError, TypeError, LookupError):
        logger.warning("Could not decode an email header.")
        return value.strip()


def decode_body_data(data: str, charset: str | None = None) -> str:
    """Decode Gmail Base64URL-encoded message content."""

    try:
        padding = "=" * (-len(data) % 4)
        raw_bytes = base64.urlsafe_b64decode(data + padding)

        if charset:
            try:
                return raw_bytes.decode(charset)
            except LookupError:
                logger.warning(
                    "Unknown email charset; using UTF-8 fallback."
                )

        return raw_bytes.decode("utf-8", errors="replace")

    except (ValueError, TypeError) as exc:
        raise GmailMessageParsingError(
            "Could not decode Gmail message content."
        ) from exc


def get_header(
    headers: list[dict[str, str]],
    name: str,
) -> str | None:
    """Find a Gmail message header without case sensitivity."""

    for header in headers:
        if header.get("name", "").lower() == name.lower():
            return header.get("value")

    return None


def extract_body_parts(
    payload: dict[str, Any],
    plain_parts: list[str],
    html_parts: list[str],
) -> None:
    """Recursively extract plain-text and HTML body parts."""

    mime_type = payload.get("mimeType", "")
    filename = payload.get("filename", "")
    body_data = payload.get("body", {}).get("data")

    # Do not treat downloadable attachments as email body content.
    if filename or payload.get("body", {}).get("attachmentId"):
        return

    if body_data:
        content_type = get_header(
            payload.get("headers", []),
            "Content-Type",
        )

        charset = None

        if content_type:
            match = re.search(
                r'charset=["\']?([^;"\']+)',
                content_type,
                re.IGNORECASE,
            )
            if match:
                charset = match.group(1).strip()

        decoded = decode_body_data(body_data, charset)

        if mime_type == "text/plain":
            plain_parts.append(decoded)

        elif mime_type == "text/html":
            html_parts.append(decoded)

    for part in payload.get("parts", []):
        extract_body_parts(part, plain_parts, html_parts)


def html_to_text(html: str) -> str:
    """Convert HTML content into readable text."""

    extractor = HTMLTextExtractor()

    try:
        extractor.feed(html)
        extractor.close()
        return extractor.get_text()

    except Exception as exc:
        raise GmailMessageParsingError(
            "Could not extract text from HTML email content."
        ) from exc


def extract_email_body(payload: dict[str, Any]) -> str:
    """Prefer plain text and fall back to HTML."""

    plain_parts: list[str] = []
    html_parts: list[str] = []

    extract_body_parts(payload, plain_parts, html_parts)

    if plain_parts:
        body = clean_body("\n\n".join(plain_parts))

        if body:
            return body

    if html_parts:
        body = html_to_text("\n\n".join(html_parts))

        if body:
            return body

    raise GmailMessageParsingError(
        "Gmail message does not contain a readable email body."
    )


def parse_gmail_message(
    message: dict[str, Any],
) -> ParsedGmailEmail:
    """Convert a full Gmail API message resource into a normalized email."""

    try:
        message_id = message.get("id")
        thread_id = message.get("threadId")
        payload = message.get("payload", {})
        headers = payload.get("headers", [])

        sender_header = decode_header_value(
            get_header(headers, "From")
        )

        _, sender = parseaddr(sender_header)

        subject = (
                decode_header_value(get_header(headers, "Subject"))
                or "(No subject)"
        )

        if not sender or not subject:
            raise GmailMessageParsingError(
                "Gmail message is missing its sender or subject."
            )

        body = extract_email_body(payload)

        internal_date = message.get("internalDate")
        received_at = None

        if internal_date is not None:
            received_at = datetime.fromtimestamp(
                int(internal_date) / 1000,
                tz=timezone.utc,
            )

        if len(body) > 10000:
            raise GmailMessageParsingError(
                "Email body exceeds the maximum supported length."
            )

        email_adapter = TypeAdapter(EmailStr)
        validated_sender = email_adapter.validate_python(sender)

        return ParsedGmailEmail(
            gmail_message_id=message_id,
            thread_id=thread_id,
            sender=validated_sender,
            subject=subject,
            body=body,
            received_at=received_at,
        )

    except GmailMessageParsingError:
        raise

    except (KeyError, TypeError, ValueError, ValidationError) as exc:
        logger.warning("Gmail message could not be normalized.")

        raise GmailMessageParsingError(
            "Gmail message has an invalid structure or content."
        ) from exc
