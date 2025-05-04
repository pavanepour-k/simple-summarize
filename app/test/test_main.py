from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_integration():
    # API 호출 및 파일 업로드 통합 테스트
    # 텍스트 요약 및 파일 업로드 동시 수행
    response = client.post(
        "/summarize", 
        json={"content": "This is a test sentence for integration.", "option": "medium", "style": "problem_solver"}
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
    assert "file_url" in response.json()  # 업로드된 파일 URL이 반환되어야 함
