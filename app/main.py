from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import os
from dotenv import load_dotenv
from app.api.summarize_router import user_router
from app.api.admin_router import admin_router
from app.config.settings import settings

# 로거 초기화
logger = logging.getLogger(__name__)

# 환경 변수 로드
load_dotenv()

# 환경 변수가 제대로 로드되었는지 점검
def check_env_variables():
    required_vars = ["PRIVATE_KEY", "PUBLIC_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        for var in missing_vars:
            logger.warning(f"Warning: {var} is not set in the environment variables.")
        return False
    return True

# 환경 변수 체크
if not check_env_variables():
    logger.warning("Some environment variables are missing. Please check your .env file.")

# FastAPI 애플리케이션 생성
app = FastAPI(
    title=settings.API_NAME,
    version="1.0",
    description="API for text summarization with support for multiple languages and styles"
)

# 로깅 설정
log_level = logging.DEBUG if settings.DEBUG_MODE else logging.INFO
logging.basicConfig(
    level=log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# 파일 크기 제한 설정 (MB -> Byte)
MAX_FILE_SIZE = settings.MAX_FILE_SIZE_MB * 1024 * 1024

# 파일 크기 검사 미들웨어
@app.middleware("http")
async def limit_file_size(request: Request, call_next):
    if request.method == "POST" and "multipart/form-data" in request.headers.get("Content-Type", ""):
        form_data = await request.form()
        for field in form_data.values():
            if hasattr(field, 'filename'):
                file_content = await field.read()
                file_size = len(file_content)
                if file_size > MAX_FILE_SIZE:
                    return JSONResponse(
                        status_code=413,
                        content={"detail": f"File too large. Maximum size is {settings.MAX_FILE_SIZE_MB} MB."}
                    )
    return await call_next(request)

# 예외 처리 미들웨어
@app.middleware("http")
async def exception_handling_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except HTTPException as e:
        logger.error(f"HTTP Exception: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=e.status_code,
            content={"detail": e.detail}
        )
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "An internal server error occurred"}
        )

# CORS 미들웨어
if settings.ENVIRONMENT == "production":
    allowed_origins = [
        "https://yourtrustedwebsite.com",
        "https://anothertrustedwebsite.com"
    ]
else:
    allowed_origins = ["http://localhost", "http://127.0.0.1"] 

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # 로컬에서만 허용
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)

# 라우터 등록
app.include_router(user_router, prefix="/summarize", tags=["Summarization"])
app.include_router(admin_router)

# 상태 체크 엔드포인트
@app.get("/", tags=["Health"])
async def root():
    """API 상태 체크 엔드포인트"""
    return {"status": "healthy", "api": settings.API_NAME, "version": "1.0"}

# 스타트업 이벤트
@app.on_event("startup")
async def startup_event():
    """앱 스타트업 시 서비스 초기화"""
    logger.info(f"Starting {settings.API_NAME}")

# 셧다운 이벤트
@app.on_event("shutdown")
async def shutdown_event():
    """앱 종료 시 리소스 정리"""
    logger.info(f"Shutting down {settings.API_NAME}")
