from fastapi import FastAPI, HTTPException, Request
from dotenv import load_dotenv
import logging
import os
from app.api.summarize_router import router as summarize_router
from app.api.admin_router import admin_router  # admin_router 임포트
from app.config.settings import settings

# .env 파일 로드
load_dotenv()

# 환경 설정에서 파일 크기 제한을 MB 단위로 읽고, 바이트 단위로 변환
def get_max_file_size() -> int:
    # 환경에 따라 다른 값 로드 가능 (기본값: 10MB)
    max_size_mb = int(os.getenv("MAX_FILE_SIZE_MB", 10))  # 기본값 10MB
    return max_size_mb * 1024 * 1024  # MB를 바이트로 변환

MAX_FILE_SIZE = get_max_file_size()  # 동적으로 파일 크기 제한 설정

# FastAPI 인스턴스 생성
app = FastAPI(
    title=settings.API_NAME,
    version="1.0"
)

# 로깅 설정
log_level = logging.DEBUG if settings.DEBUG_MODE else logging.INFO
logging.basicConfig(level=log_level)
logger = logging.getLogger(__name__)

# 업로드 파일 크기 제한 미들웨어
@app.middleware("http")
async def limit_file_size(request: Request, call_next):
    if request.method == "POST" and "Content-Type" in request.headers:
        content_type = request.headers["Content-Type"]
        if "multipart/form-data" in content_type:
            content_length = int(request.headers.get("Content-Length", 0))
            if content_length > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=413,
                    detail=f"File is too large. Maximum allowed size is {MAX_FILE_SIZE // (1024 * 1024)} MB."
                )
    response = await call_next(request)
    return response

# 요약 라우터 등록
app.include_router(summarize_router, prefix="/summarize", tags=["Summarization"])
# 관리자 라우터 등록
app.include_router(admin_router, prefix="/admin", tags=["Admin"])
