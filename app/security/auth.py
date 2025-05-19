from fastapi import Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.security.user_roles import get_user_role
from app.utils.jwt_handler import verify_jwt
from app.utils.error_handler import raise_http_exception
from app.config.settings import settings
from typing import List

security = HTTPBearer()

# API_KEY and JWT keys from environment variables
API_KEY = settings.API_KEY
SECRET_KEY = settings.SECRET_KEY
PUBLIC_KEY = settings.PUBLIC_KEY  # PUBLIC_KEY loaded from settings

# Example external API keys
VALID_API_KEYS: List[str] = ["valid_api_key_1", "valid_api_key_2"]


# API key verification
def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # Extract api_key and role from JWT for verification
    payload = verify_jwt(credentials.credentials, PUBLIC_KEY)
    api_key = payload.get("api_key")
    role = payload.get("role")

    if not api_key or api_key != API_KEY:
        raise_http_exception(
            "Invalid or missing API key", code=status.HTTP_401_UNAUTHORIZED
        )

    if api_key not in VALID_API_KEYS:
        raise_http_exception(
            "API key is not authorized", code=status.HTTP_401_UNAUTHORIZED
        )

    if role not in ["user", "admin"]:  # Example role validation
        raise_http_exception("Invalid role", code=status.HTTP_403_FORBIDDEN)

    return api_key


# User access verification
def verify_user_access(api_key: str = Depends(verify_api_key)):
    role = get_user_role(api_key)
    if role == "admin":
        raise_http_exception(
            "Admin cannot access user API", code=status.HTTP_403_FORBIDDEN
        )
    return True


# Admin access verification
def verify_admin(api_key: str = Depends(verify_api_key)):
    role = get_user_role(api_key)
    if role != "admin":
        raise_http_exception(
            "Admin privileges required", code=status.HTTP_403_FORBIDDEN
        )
    return True
