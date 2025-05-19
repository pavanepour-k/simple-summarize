from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.security.user_roles import get_user_role
from app.utils.jwt_handler import verify_jwt
from app.utils.error_handler import raise_http_exception
from app.config.settings import settings
from typing import List

security = HTTPBearer()

# 환경 변수로 설정된 API_KEY와 JWT 비밀키/공개키 경로
API_KEY = settings.API_KEY
SECRET_KEY = settings.SECRET_KEY
PUBLIC_KEY = settings.PUBLIC_KEY  # PUBLIC_KEY를 settings에서 로드

# 외부 API 키 목록 (예시)
VALID_API_KEYS: List[str] = ["valid_api_key_1", "valid_api_key_2"]

# API 키 인증
def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # JWT에서 api_key와 role을 추출하여 검증
    payload = verify_jwt(credentials.credentials, PUBLIC_KEY)
    api_key = payload.get("api_key")
    role = payload.get("role")
    
    if not api_key or api_key != API_KEY:
        raise_http_exception("Invalid or missing API key", code=status.HTTP_401_UNAUTHORIZED)

    if api_key not in VALID_API_KEYS:
        raise_http_exception("API key is not authorized", code=status.HTTP_401_UNAUTHORIZED)

    # 추가적인 API 키나 역할 검증 로직을 여기에 추가할 수 있습니다.
    if role not in ["user", "admin"]:  # 예시 역할 검증
        raise_http_exception("Invalid role", code=status.HTTP_403_FORBIDDEN)
    
    return api_key

# 사용자 인증 (사용자 전용)
def verify_user_access(api_key: str = Depends(verify_api_key)):
    role = get_user_role(api_key)
    if role == "admin":
        raise_http_exception("Admin cannot access user API", code=status.HTTP_403_FORBIDDEN)
    return True

# 관리자 인증
def verify_admin(api_key: str = Depends(verify_api_key)):
    role = get_user_role(api_key)
    if role != "admin":
        raise_http_exception("Admin privileges required", code=status.HTTP_403_FORBIDDEN)
    return True
