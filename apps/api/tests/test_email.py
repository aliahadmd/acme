from app.services import email_service
from app.services.email_service import build_message


def test_build_message_sets_headers() -> None:
    msg = build_message(to="ada@example.com", subject="Hello", html="<b>Hi</b>")
    assert msg["To"] == "ada@example.com"
    assert msg["Subject"] == "Hello"
    assert msg["From"] == "acme@localhost"  # default smtp_from from Settings


def test_build_message_has_html_and_text_parts() -> None:
    msg = build_message(to="a@b.c", subject="s", html="<b>Hi</b>", text="Hi")
    parts = [part.get_content_subtype() for part in msg.walk() if not part.is_multipart()]
    assert "plain" in parts
    assert "html" in parts


def test_send_email_uses_mailpit_defaults(monkey_patch: None = None) -> None:
    # Config defaults must point at Mailpit (compose.yaml), not a real SMTP server.
    assert email_service.get_settings().smtp_host == "localhost"
    assert email_service.get_settings().smtp_port == 1025
    assert email_service.get_settings().smtp_use_tls is False
