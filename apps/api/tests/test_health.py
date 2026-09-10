from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_returns_ok() -> None:
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok", "environment": "local"}


def test_openapi_schema_is_served() -> None:
    res = client.get("/openapi.json")
    assert res.status_code == 200
    assert "listUsers" in res.json()["paths"]["/api/users"]["get"]["operationId"]
