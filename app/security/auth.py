from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.security.user_roles import get_user_role
from app.utils.jwt_handler import verify_jwt
from app.utils.error_handler import raise_http_exception

security = HTTPBearer()

def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    api_key = verify_jwt(credentials.credentials)
    if not api_key:
        raise_http_exception("Invalid or missing API key", code=status.HTTP_401_UNAUTHORIZED)
    return api_key

def verify_user_access(api_key: str = Depends(verify_api_key)):
    role = get_user_role(api_key)
    from app.services.limiter import check_rate_limit
    check_rate_limit(api_key, role)
    return True

def verify_admin(api_key: str = Depends(verify_api_key)):
    role = get_user_role(api_key)
    if role != "admin":
        raise_http_exception("Admin privileges required", code=status.HTTP_403_FORBIDDEN)
    return True