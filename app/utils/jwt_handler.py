from jose import JWTError, jwt
from app.config.settings import settings
from app.utils.error_handler import raise_http_exception

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"

def verify_jwt(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("api_key")
    except JWTError:
        raise_http_exception("Invalid JWT token", code=401)