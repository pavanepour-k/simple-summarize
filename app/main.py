from fastapi import FastAPI, HTTPException, Request
from dotenv import load_dotenv
import logging
from app.api.summarize_router import router as summarize_router
from app.config.settings import settings

# .env 파일 로드
load_dotenv()

# FastAPI 인스턴스 생성
app = FastAPI(
    title=settings.API_NAME,
    version="1.0"
)

# 로깅 설정
log_level = logging.DEBUG if settings.DEBUG_MODE else logging.INFO
logging.basicConfig(level=log_level)
logger = logging.getLogger(__name__)

# 업로드 파일 크기 제한 미들웨어 (10MB 제한)
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

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
