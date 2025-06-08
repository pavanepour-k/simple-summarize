from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Test valid JWT token
def test_valid_jwt():
    response = client.get(
        "/summarize", headers={"Authorization": f"Bearer {valid_token}"}
    )
    assert response.status_code == 200

# Test invalid JWT token
def test_invalid_jwt():
    response = client.get(
        "/summarize", headers={"Authorization": f"Bearer {invalid_token}"}
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid JWT token"}
