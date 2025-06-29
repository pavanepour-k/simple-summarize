"""HTTP middleware functions."""
from __future__ import annotations

import logging

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

from app.config.settings import get_settings

logger = logging.getLogger(__name__)


async def file_size_limit_middleware(request: Request, call_next):
    """Enforce maximum file upload size.
    
    Args:
        request: HTTP request
        call_next: Next middleware/handler
        
    Returns:
        HTTP response
    """
    settings = get_settings()
    max_size = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    
    if (request.method == "POST" and 
        "multipart/form-data" in request.headers.get("Content-Type", "")):
        content_length = int(request.headers.get("Content-Length", 0))
        if content_length > max_size:
            return JSONResponse(
                status_code=413,
                content={
                    "detail": f"File too large. Maximum size is {settings.MAX_FILE_SIZE_MB} MB."
                }
            )
    
    return await call_next(request)


async def exception_handling_middleware(request: Request, call_next):
    """Handle exceptions across all routes.
    
    Args:
        request: HTTP request
        call_next: Next middleware/handler
        
    Returns:
        HTTP response
    """
    try:
        return await call_next(request)
    except HTTPException as e:
        logger.error(f"HTTP Exception: {e.detail}", exc_info=True)
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