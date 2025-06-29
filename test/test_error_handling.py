from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Test invalid file type response
def test_invalid_file_type():
    data = {
        "content": "This is a test text",
        "option": "medium",
        "style": "general"
    }
    response = client.post(
        "/summarize", json=data, headers={"Content-Type": "application/xml"}
    )
    assert response.status_code == 415
    assert response.json() == {
        "detail": "Unsupported file type. Allowed formats: .pdf, .docx, .txt, .md"
    }
