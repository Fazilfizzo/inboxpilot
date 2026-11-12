
import logging
from typing import Any

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.core.config import settings
from app.integrations.gmail.auth import get_gmail_credentials
from app.integrations.gmail.exceptions import (
    GmailConnectionError,
    GmailMessageNotFoundError,
)

logger = logging.getLogger(__name__)


class GmailClient:
    """Client for retrieving messages from a Gmail mailbox."""

    def __init__(self) -> None:
        credentials = get_gmail_credentials()

        self._service = build(
            "gmail",
            "v1",
            credentials=credentials,
            cache_discovery=False,
        )

    def get_profile(self) -> dict[str, Any]:
        """Return basic information about the authenticated Gmail account."""

        try:
            return (
                self._service.users()
                .getProfile(userId="me")
                .execute()
            )

        except HttpError as exc:
            logger.exception("Could not retrieve Gmail profile.")
            raise GmailConnectionError(
                "Could not retrieve Gmail profile."
            ) from exc

    def list_messages(
            self,
            query: str | None = None,
            max_results: int | None = None,
    ) -> list[dict[str, str]]:
        """Retrieve matching Gmail message IDs and thread IDs."""
        resolved_query = (
            settings.gmail_query if query is None else query
        )
        resolved_max_results = (
            settings.gmail_max_results
            if max_results is None
            else max_results
        )

        if resolved_max_results < 1:
            raise ValueError("max_results must be positive.")

        try:
            response = (
                self._service.users()
                .messages()
                .list(
                    userId="me",
                    q=resolved_query,
                    maxResults=resolved_max_results,
                )
                .execute()
            )

            return response.get("messages", [])

        except HttpError as exc:
            logger.exception("Could not list Gmail messages.")
            raise GmailConnectionError(
                "Could not retrieve Gmail messages."
            ) from exc

    def get_message(
        self,
        message_id: str,
    ) -> dict[str, Any]:
        """Retrieve the full Gmail message resource."""

        if not message_id.strip():
            raise ValueError("message_id cannot be empty.")

        try:
            return (
                self._service.users()
                .messages()
                .get(
                    userId="me",
                    id=message_id,
                    format="full",
                )
                .execute()
            )

        except HttpError as exc:
            if exc.resp.status == 404:
                raise GmailMessageNotFoundError(
                    f"Gmail message not found: {message_id}"
                ) from exc

            logger.exception(
                "Could not retrieve Gmail message."
            )

            raise GmailConnectionError(
                "Could not retrieve Gmail message."
            ) from exc
