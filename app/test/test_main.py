from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Test integration of API call and file upload
def test_integration():
    response = client.post(
        "/summarize", 
        json={"content": "This is a test sentence for integration.", "option": "medium", "style": "problem_solver"}
        ,headers={"Authorization": "Bearer valid_token"}
    )
    assert response.status_code == 200
    assert "summary" in response.json()

    with open("test_file.txt", "w") as f:
        f.write("This is a test file content.")

    with open("test_file.txt", "rb") as f:
        response = client.post(
            "/upload", 
            files={"file": ("test_file.txt", f, "text/plain")}
        )
    assert response.status_code == 200
    assert "file_url" in response.json()  # Ensure file URL is returned
