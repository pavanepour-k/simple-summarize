"""FastAPI application entry point."""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.admin_router import admin_router
from app.api.summarize_router import user_router
from app.config.settings import get_settings
from app.utils.middleware import (
    exception_handling_middleware,
    file_size_limit_middleware
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler.
    
    Args:
        app: FastAPI application instance
        
    Yields:
        None
    """
    settings = get_settings()
    logger.info(f"Starting {settings.API_NAME}")
    yield
    logger.info(f"Shutting down {settings.API_NAME}")


def create_app() -> FastAPI:
    """Create and configure FastAPI application.
    
    Returns:
        Configured FastAPI instance
    """
    settings = get_settings()
    
    # Configure logging
    log_level = logging.DEBUG if settings.DEBUG_MODE else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    app = FastAPI(
        title=settings.API_NAME,
        version="1.0",
        description="API for text summarization with multiple languages and styles",
        lifespan=lifespan
    )
    
    # Add middlewares
    app.middleware("http")(file_size_limit_middleware)
    app.middleware("http")(exception_handling_middleware)
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )
    
    # Include routers
    app.include_router(user_router, prefix="/summarize", tags=["Summarization"])
    app.include_router(admin_router)
    
    # Add health check endpoint
    @app.get("/", tags=["Health"])
    async def health_check() -> dict:
        """Health check endpoint.
        
        Returns:
            Service status information
        """
        return {
            "status": "healthy",
            "api": settings.API_NAME,
            "version": "1.0"
        }
    
    return app


app = create_app()