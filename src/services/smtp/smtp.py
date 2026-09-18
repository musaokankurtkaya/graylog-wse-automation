import os
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from functools import lru_cache

from jinja2 import (
    Environment,
    FileSystemLoader,
    Template,
    TemplateNotFound,
    select_autoescape,
)

from src.utils.logger import log_message


class SMTP(smtplib.SMTP):
    def __init__(self, host: str = "smtp.gmail.com", port: int = 587, **kwargs) -> None:
        super().__init__(host=host, port=port, **kwargs)

    def _login(self, user: str, password: str) -> bool:
        """Log in to the smtp server with the provided user and password."""

        try:
            self.starttls()
            super().login(user=user, password=password)
            self.from_email: str = user
            log_message(mode="info", msg=f"authentication successful for ⊱ {user} ⊰")
            return True
        except smtplib.SMTPAuthenticationError:
            log_message(mode="error", msg=f"authentication failed for ⊱ {user} ⊰")
            return False

    def _sendmail(
        self,
        subject: str,
        message: str,
        to_email: str,
        cc: str | None = None,
        attachment: str | None = None,
    ) -> None:
        """Send an email via smtp with the provided subject, message, and email addresses."""

        msg: MIMEMultipart = MIMEMultipart()

        msg["Subject"] = subject

        to_addrs: list[str] = self._parse_email_addrs(email_addrs=to_email)
        if cc:
            msg["Cc"] = cc
            to_addrs += self._parse_email_addrs(email_addrs=cc)

        msg.attach(payload=MIMEText(_text=message, _subtype="html", _charset="utf-8"))

        if attachment:
            if not os.path.isfile(path=attachment):
                log_message(
                    mode="error",
                    msg=f"⊱ {attachment} ⊰ file not found, skipping attachment",
                )
                return

            attachment_name: str = os.path.basename(attachment)
            with open(file=attachment, mode="rb") as f:
                part = MIMEBase(_maintype="application", _subtype="octet-stream")
                part.set_payload(payload=f.read())
                encoders.encode_base64(msg=part)
                part.add_header(
                    _name="content-disposition",
                    _value="attachment",
                    filename=attachment_name,
                )
                msg.attach(payload=part)

        try:
            self.sendmail(
                from_addr=self.from_email, to_addrs=to_addrs, msg=msg.as_string()
            )
            log_message(
                mode="info", msg=f"mail sent successfully to ⊱ {', '.join(to_addrs)} ⊰"
            )
            os.remove(path=attachment) if attachment else None
        except smtplib.SMTPException as e:
            log_message(
                mode="error",
                msg=f"error ⊱ {e} ⊰ occured while sending mail to ⊱ {', '.join(to_addrs)} ⊰",
            )

    @staticmethod
    @lru_cache(maxsize=1)
    def load_mail_template() -> Template | None:
        """Load the mail template from the templates/ directory."""

        template_path: str = os.path.join(os.path.dirname(__file__), "templates")
        env: Environment = Environment(
            loader=FileSystemLoader(searchpath=template_path),
            autoescape=select_autoescape(
                enabled_extensions=(), disabled_extensions=("html", "htm", "xml")
            ),
        )

        template_file_name: str = "mail_template.html"
        try:
            template: Template = env.get_template(name=template_file_name)
            return template
        except TemplateNotFound:
            log_message(
                mode="error",
                msg=f"⊱ {template_file_name} ⊰ file not found in ⊱ {template_path} ⊰",
            )

    @staticmethod
    def _parse_email_addrs(email_addrs: str) -> list[str]:
        """Parse a string of email addresses separated by commas into a list.

        Examples
        --------
        >>> SMTP._parse_email_addrs(email_addrs="test@test.com, test2@test.com, test3@test.com")
        ... ['test@test.com', 'test2@test.com', 'test3@test.com']
        """

        return [email_addr.strip() for email_addr in email_addrs.split(",")]

    def _quit(self) -> None:
        try:
            super().quit()
            log_message(mode="info", msg="SMTP session terminated successfully")
        except smtplib.SMTPException as e:
            log_message(
                mode="error",
                msg=f"error ⊱ {e} ⊰ occured while terminating the SMTP session",
            )
