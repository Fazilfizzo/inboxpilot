
import sqlite3
from pathlib import Path


class EmailDeduplicationRepository:
    """Persist Gmail message processing records."""

    def __init__(self, database_path: Path) -> None:
        self._database_path = database_path
        self._database_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        self._initialize_database()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(
            self._database_path,
            timeout=10,
        )
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize_database(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS processed_emails (
                    gmail_message_id TEXT PRIMARY KEY,
                    thread_id TEXT NOT NULL,
                    status TEXT NOT NULL CHECK (
                        status IN ('processing', 'processed', 'failed')
                    ),
                    attempt_count INTEGER NOT NULL DEFAULT 1,
                    last_error TEXT,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    processed_at TEXT
                )
                """
            )

    def claim_message(
        self,
        gmail_message_id: str,
        thread_id: str,
    ) -> bool:
        """
        Atomically claim a Gmail message for processing.

        Returns True for a new or retryable failed message.
        Returns False if the message is already processing or processed.
        """
        if not gmail_message_id.strip():
            raise ValueError("Gmail message ID cannot be empty.")

        if not thread_id.strip():
            raise ValueError("Gmail thread ID cannot be empty.")

        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")

            existing = connection.execute(
                """
                SELECT status
                FROM processed_emails
                WHERE gmail_message_id = ?
                """,
                (gmail_message_id,),
            ).fetchone()

            if existing is None:
                connection.execute(
                    """
                    INSERT INTO processed_emails (
                        gmail_message_id,
                        thread_id,
                        status
                    )
                    VALUES (?, ?, 'processing')
                    """,
                    (gmail_message_id, thread_id),
                )
                return True

            if existing["status"] == "failed":
                connection.execute(
                    """
                    UPDATE processed_emails
                    SET status = 'processing',
                        attempt_count = attempt_count + 1,
                        last_error = NULL,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE gmail_message_id = ?
                    """,
                    (gmail_message_id,),
                )
                return True

            return False

    def mark_processed(self, gmail_message_id: str) -> None:
        """Mark an email as successfully processed."""
        with self._connect() as connection:
            cursor = connection.execute(
                """
                UPDATE processed_emails
                SET status = 'processed',
                    processed_at = CURRENT_TIMESTAMP,
                    updated_at = CURRENT_TIMESTAMP,
                    last_error = NULL
                WHERE gmail_message_id = ?
                  AND status = 'processing'
                """,
                (gmail_message_id,),
            )

            if cursor.rowcount == 0:
                raise ValueError(
                    f"Email is not currently processing: {gmail_message_id}"
                )

    def mark_failed(
        self,
        gmail_message_id: str,
        error_message: str,
    ) -> None:
        """Record a processing failure."""
        with self._connect() as connection:
            cursor = connection.execute(
                """
                UPDATE processed_emails
                SET status = 'failed',
                    last_error = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE gmail_message_id = ?
                  AND status = 'processing'
                """,
                (error_message, gmail_message_id),
            )

            if cursor.rowcount == 0:
                raise ValueError(
                    f"Email is not currently processing: {gmail_message_id}"
                )

    def get_status(self, gmail_message_id: str) -> str | None:
        """Retrieve the current processing status."""
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT status
                FROM processed_emails
                WHERE gmail_message_id = ?
                """,
                (gmail_message_id,),
            ).fetchone()

        return row["status"] if row else None
