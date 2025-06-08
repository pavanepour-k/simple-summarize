from fastapi import FastAPI, Request, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import os
from app.api.summarize_router import user_router
from app.api.admin_router import admin_router
from app.config.settings import settings

# Load environment variables from .env file
from dotenv import load_dotenv

load_dotenv()

# Initialize logger for this module
logger = logging.getLogger(__name__)

# Check if required environment variables are loaded
def check_env_variables() -> bool:
    required = ("PRIVATE_KEY", "PUBLIC_KEY")
    missing = [var for var in required if os.getenv(var) is None]
    for var in missing:
        logger.warning("%s is not set in environment variables", var)
    return not missing

# Warn if any required environment variables are missing
test_env_ok = check_env_variables()
if not test_env_ok:
    logger.warning("Some environment variables are missing. Please verify your .env file.")

# Create FastAPI application instance
app = FastAPI(
    title=settings.API_NAME,
    version="1.0",
    description="API for text summarization with support for multiple languages and styles",
)

# Configure logging level based on debug mode
log_level = logging.DEBUG if settings.DEBUG_MODE else logging.INFO
logging.basicConfig(
    level=log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="app.log",
)

# File size limit from settings (in bytes)
MAX_FILE_SIZE = settings.MAX_FILE_SIZE_MB * 1024 * 1024

# Middleware to enforce maximum file upload size
@app.middleware("http")
async def limit_file_size(request: Request, call_next):
    if request.method == "POST" and "multipart/form-data" in request.headers.get(
        "Content-Type", ""
    ):
        content_length = int(request.headers.get("Content-Length", 0))
        if content_length > MAX_FILE_SIZE:
            return JSONResponse(
                status_code=413,
                content={
                    "detail": (
                        f"File too large. Maximum size is {settings.MAX_FILE_SIZE_MB} MB."
                    )
                },
            )
    return await call_next(request)

# Middleware for exception handling across all routes
@app.middleware("http")
async def exception_handling_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except HTTPException as e:
        logger.error(f"HTTP Exception: {e.detail}", exc_info=True)
        return JSONResponse(
            status_code=e.status_code,
            content={"detail": e.detail},
        )
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "An internal server error occurred"},
        )

# CORS middleware: allow all origins (restrict in production!)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # allow all HTTP methods
    allow_headers=["*"],  # allow all headers
)

# Register routers for summarization and admin APIs
app.include_router(user_router, prefix="/summarize", tags=["Summarization"])
app.include_router(admin_router)  # Admin router includes its own prefix

# Simple summarize endpoint for testing purposes
@app.post("/summarize")
async def summarize(data: dict):
    text = data.get("content", "")
    summary = text[:50]
    logger.info("/summarize endpoint called")
    return {"summary": summary, "summary_text": summary}

# Simple file upload endpoint for testing purposes
@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        return JSONResponse(
            status_code=413,
            content={"detail": f"File is too large. Maximum size is {settings.MAX_FILE_SIZE_MB} MB."},
        )
    os.makedirs("uploads", exist_ok=True)
    file_path = os.path.join("uploads", file.filename)
    with open(file_path, "wb") as f:
        f.write(contents)
    logger.info("File uploaded: %s", file.filename)
    return {"file_url": file_path}

# Test endpoint for logging
@app.get("/some-endpoint")
async def some_endpoint():
    logger.info("/some-endpoint accessed")
    return {"message": "ok"}

# Health check endpoint
@app.get("/", tags=["Health"])
async def root():
    # Returns the service status and version info
    return {"status": "healthy", "api": settings.API_NAME, "version": "1.0"}

# Application startup event handler
@app.on_event("startup")
async def startup_event():
    logger.info(f"Starting {settings.API_NAME}")

# Application shutdown event handler
@app.on_event("shutdown")
async def shutdown_event():
    logger.info(f"Shutting down {settings.API_NAME}")
    # Place additional cleanup logic here
