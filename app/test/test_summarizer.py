import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_api_summarization():
    # 요약 API 호출 테스트
    response = client.post(
        "/summarize", 
        json={"content": "This is a test sentence.", "option": "short", "style": "general"}
    )
    assert response.status_code == 200
    assert "summary" in response.json()  # 응답에 'summary' 필드가 있어야 함
    assert len(response.json()["summary"]) > 0  # 요약된 내용이 있어야 함

def test_file_upload():
    # 파일 업로드 크기 제한 테스트
    with open("test_file.txt", "w") as f:
        f.write("This is a test file content.")
    
    with open("test_file.txt", "rb") as f:
        response = client.post(
            "/upload", 
            files={"file": ("test_file.txt", f, "text/plain")}
        )
    assert response.status_code == 200  # 업로드 성공
    assert "file_url" in response.json()  # 업로드된 파일 URL이 반환되어야 함
