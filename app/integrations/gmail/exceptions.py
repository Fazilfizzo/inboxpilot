
class GmailIntegrationError(Exception):
    """Base exception for Gmail integration failures."""


class GmailAuthenticationError(GmailIntegrationError):
    """Gmail OAuth authentication failed."""


class GmailConfigurationError(GmailIntegrationError):
    """Gmail integration configuration is invalid."""


class GmailConnectionError(GmailIntegrationError):
    """Could not communicate with the Gmail API."""


class GmailMessageNotFoundError(GmailIntegrationError):
    """Requested Gmail message does not exist."""


class GmailMessageParsingError(GmailIntegrationError):
    """Gmail message could not be parsed."""
