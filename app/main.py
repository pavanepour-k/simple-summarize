from fastapi import FastAPI, HTTPException, Request
<<<<<<< HEAD
from dotenv import load_dotenv
import logging
import os
from app.api.summarize_router import user_router
from app.api.admin_router import admin_router  # admin_router 임포트
=======
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import os
from app.api.summarize_router import user_router
from app.api.admin_router import admin_router
>>>>>>> dev
from app.config.settings import settings

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

<<<<<<< HEAD
# 환경 설정에서 파일 크기 제한을 MB 단위로 읽고, 바이트 단위로 변환
def get_max_file_size() -> int:
    # .env 파일에서 MAX_FILE_SIZE_MB 값을 읽어옵니다. 기본값은 10MB로 설정
    max_size_mb = int(os.getenv("MAX_FILE_SIZE_MB", 10))  # 기본값 10MB
    return max_size_mb * 1024 * 1024  # MB를 바이트로 변환

MAX_FILE_SIZE = get_max_file_size()  # 동적으로 파일 크기 제한 설정

# FastAPI 인스턴스 생성
=======
# Create FastAPI application
>>>>>>> dev
app = FastAPI(
    title=settings.API_NAME,
    version="1.0",
    description="API for text summarization with support for multiple languages and styles"
)

<<<<<<< HEAD
# 로깅 설정
=======
# Set up logging
>>>>>>> dev
log_level = logging.DEBUG if settings.DEBUG_MODE else logging.INFO
logging.basicConfig(
    level=log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

<<<<<<< HEAD
# 업로드 파일 크기 제한 미들웨어
@app.middleware("http")
async def limit_file_size(request: Request, call_next):
    # POST 요청에 대해 파일 크기 제한을 검사합니다.
    if request.method == "POST" and "Content-Type" in request.headers:
        content_type = request.headers["Content-Type"]
        # multipart/form-data (파일 업로드 형식)일 경우에만 처리
        if "multipart/form-data" in content_type:
            content_length = int(request.headers.get("Content-Length", 0))
            # 파일 크기 제한을 초과하면 413 상태 코드와 함께 오류 메시지를 반환
            if content_length > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=413,
                    detail=f"File is too large. Maximum allowed size is {MAX_FILE_SIZE // (1024 * 1024)} MB."
                )
    response = await call_next(request)
    return response

# 요약 라우터 등록
app.include_router(user_router, prefix="/summarize", tags=["Summarization"])
# 관리자 라우터 등록
app.include_router(admin_router, prefix="/admin", tags=["Admin"])
=======
# Get file size limit from settings
MAX_FILE_SIZE = settings.MAX_FILE_SIZE_MB * 1024 * 1024  # Convert MB to bytes

# File size limiting middleware
@app.middleware("http")
async def limit_file_size(request: Request, call_next):
    if request.method == "POST" and "multipart/form-data" in request.headers.get("Content-Type", ""):
        content_length = int(request.headers.get("Content-Length", 0))
        if content_length > MAX_FILE_SIZE:
            return JSONResponse(
                status_code=413,
                content={"detail": f"File too large. Maximum size is {settings.MAX_FILE_SIZE_MB} MB."}
            )
    return await call_next(request)

# Exception handling middleware
@app.middleware("http")
async def exception_handling_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "An internal server error occurred"}
        )

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(user_router, prefix="/summarize", tags=["Summarization"])
app.include_router(admin_router)  # Admin router already has prefix

@app.get("/", tags=["Health"])
async def root():
    """API health check endpoint"""
    return {"status": "healthy", "api": settings.API_NAME, "version": "1.0"}

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info(f"Starting {settings.API_NAME}")
    # Additional startup logic could go here

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown"""
    logger.info(f"Shutting down {settings.API_NAME}")
    # Additional cleanup logic could go here
>>>>>>> dev
