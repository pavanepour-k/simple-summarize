from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from app.api.summarize_router import user_router
from app.api.admin_router import admin_router
from app.config.settings import settings

# Load environment variables
from dotenv import load_dotenv

load_dotenv()

# Create FastAPI application
app = FastAPI(
    title=settings.API_NAME,
    version="1.0",
    description="API for text summarization with support for multiple languages and styles",
)

# Set up logging
log_level = logging.DEBUG if settings.DEBUG_MODE else logging.INFO
logging.basicConfig(
    level=log_level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Get file size limit from settings
MAX_FILE_SIZE = settings.MAX_FILE_SIZE_MB * 1024 * 1024  # Convert MB to bytes


# File size limiting middleware
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


# Exception handling middleware
@app.middleware("http")
async def exception_handling_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500, content={"detail": "An internal server error occurred"}
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
    # API health check endpoint
    return {"status": "healthy", "api": settings.API_NAME, "version": "1.0"}


@app.on_event("startup")
async def startup_event():
    # Initialize services on startup
    logger.info(f"Starting {settings.API_NAME}")
    # Additional startup logic could go here


@app.on_event("shutdown")
async def shutdown_event():
    # Clean up resources on shutdown
    logger.info(f"Shutting down {settings.API_NAME}")
    # Additional cleanup logic could go here
