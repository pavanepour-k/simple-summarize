from fastapi import FastAPI, HTTPException, Request
from dotenv import load_dotenv
import os
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, Security
from app.api.summarize_router import router as summarize_router
from app.config.settings import settings

# .env 파일 로드
load_dotenv()

# FastAPI 인스턴스 생성
app = FastAPI(
    title=settings.API_NAME,
    version="1.0"
)

# API Key를 .env에서 불러오기
API_KEY = os.getenv("API_KEY")
# API Key가 없을 경우 예외 처리
if not API_KEY:
    raise ValueError("API_KEY not found in the .env file")

# 로깅 설정: DEBUG_MODE에 따라 레벨 조정
import logging
log_level = logging.DEBUG if settings.DEBUG_MODE else logging.INFO
logging.basicConfig(level=log_level)
logger = logging.getLogger(__name__)

# 인증 미들웨어
def verify_api_key(credentials: HTTPAuthorizationCredentials = Security(HTTPBearer())):
    if credentials.credentials != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key.")

# 업로드 파일 크기 제한 미들웨어 (10MB 제한)
MAX_FILE_SIZE = 10 * 1024 * 1024  # Limit: 10MB

@app.middleware("http")
async def limit_file_size(request: Request, call_next):
    if request.method == "POST" and "Content-Type" in request.headers:
        content_type = request.headers["Content-Type"]
        if "multipart/form-data" in content_type:
            content_length = int(request.headers.get("Content-Length", 0))
            if content_length > MAX_FILE_SIZE:
                raise HTTPException(status_code=413, detail="File is too large")
    response = await call_next(request)
    return response

# 요약 라우터 등록
app.include_router(summarize_router, prefix="/summarize", tags=["Summarization"])
