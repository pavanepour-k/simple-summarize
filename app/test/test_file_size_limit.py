from fastapi.testclient import TestClient
from app.main import app
import os

client = TestClient(app)

def test_file_size_limit():
    # .env 파일에서 설정된 크기보다 큰 파일 업로드 테스트
    large_file = b'a' * (10 * 1024 * 1024 + 1)  # 10MB보다 큰 파일

    response = client.post(
        "/upload", 
        files={"file": ("large_file.txt", large_file, "text/plain")}
    )
    assert response.status_code == 413  # HTTP 413 Payload Too Large 오류 발생
    assert "File is too large" in response.json()["detail"]  # 에러 메시지 확인
