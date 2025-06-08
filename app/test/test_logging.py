import logging
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Test logging functionality
def test_log_creation():
    with client:
        response = client.get("/some-endpoint")
        assert response.status_code == 200

    # Check if 'INFO' log level is present
    with open('app.log', 'r') as log_file:
        logs = log_file.read()
        assert "INFO" in logs  # Check if 'INFO' log exists
        assert "/some-endpoint accessed" in logs  # Ensure the endpoint access log exists