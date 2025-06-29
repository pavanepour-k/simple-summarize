"""Custom exception handlers and error utilities."""
from __future__ import annotations

import logging
from typing import Optional

from fastapi import HTTPException, status

logger = logging.getLogger(__name__)


class ApiError(HTTPException):
    """Base API exception."""
    
    def __init__(
        self,
        detail: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        headers: Optional[dict] = None
    ):
        super().__init__(status_code=status_code, detail={"error": detail}, headers=headers)
        logger.warning(f"API Error {status_code}: {detail}")


class BadRequestError(ApiError):
    """Bad request error (400)."""
    
    def __init__(self, detail: str):
        super().__init__(detail, status.HTTP_400_BAD_REQUEST)


class UnauthorizedError(ApiError):
    """Unauthorized error (401)."""
    
    def __init__(self, detail: str):
        super().__init__(detail, status.HTTP_401_UNAUTHORIZED)


class ForbiddenError(ApiError):
    """Forbidden error (403)."""
    
    def __init__(self, detail: str):
        super().__init__(detail, status.HTTP_403_FORBIDDEN)


class NotFoundError(ApiError):
    """Not found error (404)."""
    
    def __init__(self, detail: str):
        super().__init__(detail, status.HTTP_404_NOT_FOUND)


class InternalServerError(ApiError):
    """Internal server error (500)."""
    
    def __init__(self, detail: str):
        super().__init__(detail, status.HTTP_500_INTERNAL_SERVER_ERROR)
        logger.error(f"Internal Server Error: {detail}", exc_info=True)


def raise_http_exception(
    detail: str,
    code: int = status.HTTP_400_BAD_REQUEST,
    log_message: Optional[str] = None
) -> None:
    """Raise HTTP exception with logging.
    
    Args:
        detail: Error detail message
        code: HTTP status code
        log_message: Optional custom log message
        
    Raises:
        HTTPException: With specified code and detail
    """
    message = log_message or f"Error raised: {detail}"
    logger.warning(message)
    raise HTTPException(status_code=code, detail={"error": detail})