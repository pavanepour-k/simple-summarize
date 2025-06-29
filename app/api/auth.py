from __future__ import annotations

import time
from typing import Set

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from app.core.config import get_settings
from app.models.user import TokenPayload, UserRole

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    settings = get_settings()
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.PUBLIC_KEY,
            algorithms=["RS256"]
        )
        token_data = TokenPayload(**payload)
        if token_data.api_key != settings.API_KEY:
            raise HTTPException(401, "Invalid API key")
        return token_data.api_key
    except JWTError:
        raise HTTPException(401, "Invalid token")


def require_admin(api_key: str = Depends(verify_token)) -> str:
    if api_key != "admin_api_key":
        raise HTTPException(403, "Admin access required")
    return api_key


@router.post("/token")
async def create_token(api_key: str, role: UserRole = UserRole.USER):
    settings = get_settings()
    if api_key != settings.API_KEY:
        raise HTTPException(401, "Invalid API key")
    
    payload = {
        "api_key": api_key,
        "role": role.value,
        "exp": int(time.time()) + 3600
    }
    
    token = jwt.encode(payload, settings.PRIVATE_KEY, algorithm="RS256")
    return {"access_token": token, "token_type": "bearer"}