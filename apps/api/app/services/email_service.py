"""Transactional email over plain SMTP — provider-agnostic, stdlib only.

Dev: Mailpit catches everything (web UI http://localhost:8025, see compose.yaml).
Prod: point SMTP_* at your MTA or relay (self-hosted Stalwart/Postal on a
separate VPS, or an SMTP relay). See docs/deployment.md — never run a public
MTA on the app VPS (port 25 blocks, deliverability).
"""

import smtplib
import ssl
from email.message import EmailMessage

from app.core.config import get_settings


def build_message(
    *,
    to: str,
    subject: str,
    html: str,
    text: str | None = None,
    reply_to: str | None = None,
) -> EmailMessage:
    settings = get_settings()
    msg = EmailMessage()
    msg["From"] = settings.smtp_from
    msg["To"] = to
    msg["Subject"] = subject
    if reply_to:
        msg["Reply-To"] = reply_to
    msg.set_content(text or "This email requires an HTML-capable mail client.")
    msg.add_alternative(html, subtype="html")
    return msg


def send_email(
    *,
    to: str,
    subject: str,
    html: str,
    text: str | None = None,
    reply_to: str | None = None,
) -> None:
    msg = build_message(to=to, subject=subject, html=html, text=text, reply_to=reply_to)
    settings = get_settings()
    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15) as smtp:
        if settings.smtp_use_tls:
            smtp.starttls(context=ssl.create_default_context())
        if settings.smtp_user:
            smtp.login(settings.smtp_user, settings.smtp_password or "")
        smtp.send_message(msg)
