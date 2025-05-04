import logging
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_log_creation():
    # 로깅이 예상대로 작동하는지 확인
    with client:
        response = client.get("/some-endpoint")  # 실제 엔드포인트 호출
        assert response.status_code == 200

    # 로그가 'INFO' 수준에서 발생했다고 가정
    with open('app.log', 'r') as log_file:
        logs = log_file.read()
        assert "INFO" in logs  # 'INFO' 로그가 존재하는지 확인
        assert "some endpoint accessed" in logs  # 해당 엔드포인트 접근 로그 존재 확인
