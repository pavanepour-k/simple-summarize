"""Custom exceptions."""
from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import HTTPException


class ApiException(HTTPException):
    def __init__(
        self,
        status_code: int,
        detail: str,
        headers: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class BadRequestException(ApiException):
    def __init__(self, detail: str) -> None:
        super().__init__(status_code=400, detail=detail)


class UnauthorizedException(ApiException):
    def __init__(self, detail: str = "Unauthorized") -> None:
        super().__init__(status_code=401, detail=detail)


class ForbiddenException(ApiException):
    def __init__(self, detail: str = "Forbidden") -> None:
        super().__init__(status_code=403, detail=detail)


class NotFoundException(ApiException):
    def __init__(self, detail: str = "Not found") -> None:
        super().__init__(status_code=404, detail=detail)


class FileTooLargeException(ApiException):
    def __init__(self, max_size_mb: int) -> None:
        super().__init__(
            status_code=413,
            detail=f"File exceeds maximum size of {max_size_mb}MB"
        )


class RateLimitException(ApiException):
    def __init__(self, detail: str = "Rate limit exceeded") -> None:
        super().__init__(status_code=429, detail=detail)


class InternalServerException(ApiException):
    def __init__(self, detail: str = "Internal server error") -> None:
        super().__init__(status_code=500, detail=detail)