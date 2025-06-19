import logging
from datetime import datetime, timedelta
from typing import Dict, Optional
from jose import JWTError, ExpiredSignatureError, jwt
from app.config.settings import settings  # Load public and private keys from settings
from app.utils.error_handler import raise_http_exception
import time

# Load private and public keys
private_key = settings.PRIVATE_KEY
public_key = settings.PUBLIC_KEY  # Loaded from settings

ALGORITHM = "RS256"

# Initialize logger
logger = logging.getLogger(__name__)

def verify_jwt(token: str, key: str = public_key) -> Dict:
    try:
        # Decode the JWT token
        payload = jwt.decode(token, key, algorithms=[ALGORITHM])

        # Ensure 'api_key' exists in the payload
        if "api_key" not in payload:
            raise JWTError("api_key missing")
        
        return payload

    except ExpiredSignatureError:
        raise_http_exception("JWT token has expired", code=401)
    except JWTError as exc:
        raise_http_exception(f"Invalid JWT token: {exc}", code=401)


def create_jwt(api_key: str, role: str, expires_in: Optional[int] = 3600) -> str:
    payload = {
        "api_key": api_key,
        "role": role,  # Adding role to the payload
    }

    if expires_in is not None:
        payload["exp"] = int(time.time()) + int(expires_in)

    try:
        token = jwt.encode(payload, private_key, algorithm=ALGORITHM)
        return token
    except Exception as e:
        raise_http_exception(f"Error generating JWT: {str(e)}")
