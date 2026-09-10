from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_create_and_list_user() -> None:
    res = client.post("/api/users", json={"name": "Ada Lovelace", "email": "ada@example.com"})
    assert res.status_code == 201
    body = res.json()
    assert body["id"] == 1
    assert body["email"] == "ada@example.com"

    res = client.get("/api/users")
    assert res.status_code == 200
    payload = res.json()
    assert payload["count"] == 1
    assert payload["data"][0]["name"] == "Ada Lovelace"


def test_get_missing_user_returns_404() -> None:
    assert client.get("/api/users/999").status_code == 404
