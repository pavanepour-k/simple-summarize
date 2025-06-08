import logging
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Test logging functionality
def test_log_creation(caplog):
    with caplog.at_level(logging.INFO):
        with client:
            response = client.get("/some-endpoint")
            assert response.status_code == 200

    assert "/some-endpoint accessed" in caplog.text