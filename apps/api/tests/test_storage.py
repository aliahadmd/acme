from minio import Minio

from app.core.config import get_settings
from app.services.storage import get_s3_client, split_endpoint


def test_split_endpoint_parses_schemes() -> None:
    assert split_endpoint("http://localhost:8333") == ("localhost:8333", False)
    assert split_endpoint("https://s3.example.com") == ("s3.example.com", True)
    assert split_endpoint("s3.example.com") == ("s3.example.com", True)


def test_get_s3_client_builds_from_settings(monkeypatch) -> None:
    monkeypatch.setenv("S3_ENDPOINT", "http://localhost:8333")
    monkeypatch.setenv("S3_ACCESS_KEY", "acme")
    get_settings.cache_clear()
    get_s3_client.cache_clear()
    try:
        client = get_s3_client()
        assert isinstance(client, Minio)
    finally:
        get_settings.cache_clear()
        get_s3_client.cache_clear()
