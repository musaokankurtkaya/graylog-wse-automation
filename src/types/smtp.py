from typing import TypedDict


class SMTPConfig(TypedDict):
    """SMTP config type"""

    SMTP_HOST: str
    SMTP_PORT: str
    SMTP_FROM_EMAIL: str
    SMTP_FROM_EMAIL_APP_PASSWORD: str
    SMTP_TO_EMAILS: str
    SMTP_CC_EMAILS: str | None
