
import logging
from pathlib import Path

from google.auth.exceptions import GoogleAuthError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from app.core.config import settings
from app.integrations.gmail.exceptions import (
    GmailAuthenticationError,
    GmailConfigurationError,
)

logger = logging.getLogger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly"
]


def get_gmail_credentials() -> Credentials:
    credentials_path = settings.gmail_credentials_file
    token_path = settings.gmail_token_file

    if not credentials_path.is_file():
        raise GmailConfigurationError(
            f"Gmail credentials file not found: {credentials_path}"
        )

    credentials = None

    try:
        if token_path.is_file():
            credentials = Credentials.from_authorized_user_file(
                str(token_path),
                SCOPES,
            )

        if credentials and credentials.valid:
            return credentials

        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())

        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(credentials_path),
                SCOPES,
            )

            credentials = flow.run_local_server(
                host="localhost",
                port=0,
                open_browser=True,
            )

        token_path.parent.mkdir(parents=True, exist_ok=True)
        token_path.write_text(
            credentials.to_json(),
            encoding="utf-8",
        )

        logger.info("Gmail OAuth authentication successful.")

        return credentials

    except (OSError, ValueError, GoogleAuthError) as exc:
        logger.exception("Gmail OAuth authentication failed.")

        raise GmailAuthenticationError(
            "Could not authenticate with Gmail."
        ) from exc
