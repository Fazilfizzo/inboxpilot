
import pytest

from app.repositories.email_deduplication_repository import (
    EmailDeduplicationRepository,
)


@pytest.fixture
def repository(tmp_path):
    database_path = tmp_path / "test_mail_genius.db"
    return EmailDeduplicationRepository(database_path)


def test_claim_new_message(repository):
    result = repository.claim_message(
        "message001",
        "thread001",
    )

    assert result is True
    assert repository.get_status("message001") == "processing"


def test_prevent_duplicate_message_claim(repository):
    repository.claim_message("message001", "thread001")

    result = repository.claim_message(
        "message001",
        "thread001",
    )

    assert result is False


def test_processed_message_cannot_be_claimed_again(repository):
    repository.claim_message("message001", "thread001")
    repository.mark_processed("message001")

    result = repository.claim_message(
        "message001",
        "thread001",
    )

    assert result is False
    assert repository.get_status("message001") == "processed"


def test_failed_message_can_be_retried(repository):
    repository.claim_message("message001", "thread001")
    repository.mark_failed("message001", "Gemini timeout")

    result = repository.claim_message(
        "message001",
        "thread001",
    )

    assert result is True
    assert repository.get_status("message001") == "processing"


def test_empty_message_id_is_rejected(repository):
    with pytest.raises(ValueError):
        repository.claim_message("", "thread001")


def test_empty_thread_id_is_rejected(repository):
    with pytest.raises(ValueError):
        repository.claim_message("message001", "")
