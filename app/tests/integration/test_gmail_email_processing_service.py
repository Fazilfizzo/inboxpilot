
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.repositories.email_deduplication_repository import (
    EmailDeduplicationRepository,
)
from app.schemas.classification import ClassificationResponse
from app.schemas.email import EmailRequest
from app.services import gmail_email_processing_service as processing_module
from app.services.gmail_email_processing_service import (
    GmailEmailProcessingService,
)


@pytest.fixture
def repository(tmp_path):
    return EmailDeduplicationRepository(
        tmp_path / "test_mail_genius.db"
    )


@pytest.fixture
def gmail_client():
    client = MagicMock()

    client.list_messages.return_value = [
        {
            "id": "message001",
            "threadId": "thread001",
        }
    ]

    client.get_message.return_value = {
        "id": "message001",
        "threadId": "thread001",
    }

    return client


@pytest.fixture
def classification_service():
    service = MagicMock()

    service.classify_email = AsyncMock(
        return_value=ClassificationResponse(
            category="general",
            priority="low",
            sentiment="neutral",
            requires_human=False,
        )
    )

    return service


@pytest.fixture
def processing_service(
    gmail_client,
    repository,
    classification_service,
):
    return GmailEmailProcessingService(
        gmail_client=gmail_client,
        repository=repository,
        classification_service=classification_service,
    )


@pytest.mark.asyncio
async def test_process_new_gmail_message(
    processing_service,
    gmail_client,
    repository,
    classification_service,
    monkeypatch,
):
    monkeypatch.setattr(
        processing_module,
        "parse_gmail_message",
        lambda message: object(),
    )

    normalized_email = EmailRequest(
        sender="customer@example.com",
        subject="General question",
        body="I have a question about your service.",
    )

    monkeypatch.setattr(
        processing_module,
        "normalize_gmail_email",
        lambda email: normalized_email,
    )

    results = await processing_service.process_inbox()

    assert len(results) == 1
    assert results[0].status == "processed"
    assert results[0].gmail_message_id == "message001"

    assert repository.get_status("message001") == "processed"

    gmail_client.get_message.assert_called_once_with(
        "message001"
    )

    classification_service.classify_email.assert_awaited_once_with(
        normalized_email
    )


@pytest.mark.asyncio
async def test_skip_previously_processed_message(
    processing_service,
    gmail_client,
    repository,
    classification_service,
):
    repository.claim_message("message001", "thread001")
    repository.mark_processed("message001")

    results = await processing_service.process_inbox()

    assert len(results) == 1
    assert results[0].status == "skipped"

    gmail_client.get_message.assert_not_called()
    classification_service.classify_email.assert_not_awaited()


@pytest.mark.asyncio
async def test_mark_message_failed_when_gemini_fails(
    processing_service,
    repository,
    classification_service,
    monkeypatch,
):
    monkeypatch.setattr(
        processing_module,
        "parse_gmail_message",
        lambda message: object(),
    )

    monkeypatch.setattr(
        processing_module,
        "normalize_gmail_email",
        lambda email: EmailRequest(
            sender="customer@example.com",
            subject="Payment problem",
            body="My payment failed.",
        ),
    )

    classification_service.classify_email.side_effect = TimeoutError(
        "Gemini request timed out"
    )

    results = await processing_service.process_inbox()

    assert len(results) == 1
    assert results[0].status == "failed"
    assert results[0].error == "TimeoutError"

    assert repository.get_status("message001") == "failed"


@pytest.mark.asyncio
async def test_failed_message_can_be_retried(
    processing_service,
    repository,
    classification_service,
    monkeypatch,
):
    repository.claim_message("message001", "thread001")
    repository.mark_failed("message001", "TimeoutError")

    monkeypatch.setattr(
        processing_module,
        "parse_gmail_message",
        lambda message: object(),
    )

    monkeypatch.setattr(
        processing_module,
        "normalize_gmail_email",
        lambda email: EmailRequest(
            sender="customer@example.com",
            subject="General question",
            body="I need some help.",
        ),
    )

    results = await processing_service.process_inbox()

    assert results[0].status == "processed"
    assert repository.get_status("message001") == "processed"

    classification_service.classify_email.assert_awaited_once()
