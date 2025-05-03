import logging
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.config.settings import settings

security = HTTPBearer()
logger = logging.getLogger("uvicorn.error")

def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    API Key 검증. 유효하지 않으면 401 Unauthorized 발생.
    """
    if credentials.scheme != "Bearer" or credentials.credentials != settings.API_KEY:
        logger.warning("Unauthorized access attempt. Invalid token: %s", credentials.credentials)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "Invalid or missing API key"},
        )

def is_admin() -> bool:
    """
    .env의 API_ROLE 환경변수로부터 admin 여부 판단.
    """
    return settings.API_ROLE.lower() == "admin"

def verify_admin(api_key: None = Depends(verify_api_key)):
    """
    관리자 전용 기능 접근 권한 검증.
    관리자 로일이 아닐 경우 403 Forbidden 발생.
    """
    if not is_admin():
        logger.warning("Forbidden: Admin privilege required.")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": "Admin privileges required for this operation."},
        )
