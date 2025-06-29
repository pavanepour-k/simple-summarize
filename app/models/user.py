from __future__ import annotations

from enum import Enum

from pydantic import BaseModel


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


class TokenPayload(BaseModel):
    api_key: str
    role: UserRole
    exp: int