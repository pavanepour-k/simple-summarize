import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_summarize_text():
    response = client.post(
        "/summarize/text",
        json={
            "content": "This is a test text that needs to be summarized.",
            "style": "general",
            "length": "short"
        },
        headers={"Authorization": "Bearer test-token"}
    )
    assert response.status_code == 200
    assert "summary" in response.json()