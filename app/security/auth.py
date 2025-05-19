from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.security.user_roles import get_user_role
from app.utils.jwt_handler import verify_jwt
from app.utils.error_handler import raise_http_exception
from app.config.settings import settings  # settings 파일에서 불러오기

security = HTTPBearer()

# 환경 변수로 설정된 API_KEY와 JWT 비밀키/공개키 경로
API_KEY = settings.API_KEY
SECRET_KEY = settings.SECRET_KEY
PRIVATE_KEY_PATH = settings.PRIVATE_KEY_PATH
PUBLIC_KEY_PATH = settings.PUBLIC_KEY_PATH

# API 키 인증
def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    api_key = verify_jwt(credentials.credentials)
    if not api_key or api_key != API_KEY:
        raise_http_exception("Invalid or missing API key", code=status.HTTP_401_UNAUTHORIZED)
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
