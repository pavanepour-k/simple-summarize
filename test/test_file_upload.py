from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_file_too_large():
    # Test for uploading a file larger than the allowed size
    with open("large_test_file.txt", "w") as f:
        f.write("A" * 1024 * 1024 * 20)  # 20 MB file, assuming max allowed is 10 MB
    
    with open("large_test_file.txt", "rb") as f:
        response = client.post("/upload", files={"file": ("large_test_file.txt", f)})
        assert response.status_code == 413
        assert response.json() == {"detail": "File too large. Maximum size is 10 MB."}
