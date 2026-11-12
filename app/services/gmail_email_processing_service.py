
import logging
from dataclasses import dataclass

from app.integrations.gmail.client import GmailClient
from app.integrations.gmail.parser import parse_gmail_message
from app.repositories.email_deduplication_repository import (
    EmailDeduplicationRepository,
)
from app.schemas.classification import ClassificationResponse
from app.services.ai_classification_service import AIClassificationService
from app.services.email_normalization_service import (
    normalize_gmail_email,
)

logger = logging.getLogger(__name__)


@dataclass
class EmailProcessingResult:
    gmail_message_id: str
    status: str
    classification: ClassificationResponse | None = None
    error: str | None = None


class GmailEmailProcessingService:
    """Coordinate Gmail retrieval, deduplication and AI classification."""

    def __init__(
        self,
        gmail_client: GmailClient,
        repository: EmailDeduplicationRepository,
        classification_service: AIClassificationService,
    ) -> None:
        self._gmail_client = gmail_client
        self._repository = repository
        self._classification_service = classification_service

    async def process_inbox(
        self,
        query: str | None = None,
        max_results: int | None = None,
    ) -> list[EmailProcessingResult]:
        """Fetch and process a batch of Gmail messages."""
        messages = self._gmail_client.list_messages(
            query=query,
            max_results=max_results,
        )

        results: list[EmailProcessingResult] = []

        for message in messages:
            message_id = message.get("id")
            thread_id = message.get("threadId")

            if not message_id or not thread_id:
                logger.warning(
                    "Skipping Gmail list entry with missing identifiers."
                )
                continue

            claimed = self._repository.claim_message(
                gmail_message_id=message_id,
                thread_id=thread_id,
            )

            if not claimed:
                logger.info(
                    "Skipping previously claimed Gmail message: %s",
                    message_id,
                )
                results.append(
                    EmailProcessingResult(
                        gmail_message_id=message_id,
                        status="skipped",
                    )
                )
                continue

            try:
                raw_message = self._gmail_client.get_message(
                    message_id
                )

                parsed_email = parse_gmail_message(raw_message)

                normalized_email = normalize_gmail_email(
                    parsed_email
                )

                classification = (
                    await self._classification_service.classify_email(
                        normalized_email
                    )
                )

                self._repository.mark_processed(message_id)

                logger.info(
                    "Successfully classified Gmail message: %s",
                    message_id,
                )

                results.append(
                    EmailProcessingResult(
                        gmail_message_id=message_id,
                        status="processed",
                        classification=classification,
                    )
                )

            except Exception as exc:
                # Do not store raw exception text: it may contain
                # customer data or external API details.
                self._repository.mark_failed(
                    message_id,
                    type(exc).__name__,
                )

                logger.exception(
                    "Failed to process Gmail message: %s",
                    message_id,
                )

                results.append(
                    EmailProcessingResult(
                        gmail_message_id=message_id,
                        status="failed",
                        error=type(exc).__name__,
                    )
                )

        return results
