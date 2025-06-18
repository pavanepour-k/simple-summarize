from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_valid_jwt():
    response = client.post(
        "/summarize",
        json={"content": "hello", "option": "short", "style": "general"},
        headers={"Authorization": "Bearer valid_token"},
    )
    assert response.status_code == 200


def test_invalid_jwt():
    response = client.post(
        "/summarize",
        json={"content": "hello", "option": "short", "style": "general"},
        headers={"Authorization": "Bearer invalid_token"},
    )
    assert response.status_code == 200