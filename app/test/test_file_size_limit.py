from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Test for uploading a file larger than the size set in .env
def test_file_size_limit():
    large_file = b'a' * (10 * 1024 * 1024 + 1)  # File larger than 10MB

    response = client.post(
        "/upload", 
        files={"file": ("large_file.txt", large_file, "text/plain")}
    )
    assert response.status_code == 413  # HTTP 413 Payload Too Large error
    assert "File is too large" in response.json()["detail"]  # Check error message
