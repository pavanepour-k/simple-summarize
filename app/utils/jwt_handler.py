from jose import JWTError, jwt
from app.config.settings import settings  # Load public and private keys from settings
from app.utils.error_handler import raise_http_exception

# Load private and public keys
private_key = settings.PRIVATE_KEY
public_key = settings.PUBLIC_KEY  # Loaded from settings

ALGORITHM = "RS256"


def verify_jwt(token: str):
    # Verify JWT using the public key
    try:
        payload = jwt.decode(token, public_key, algorithms=[ALGORITHM])
        return payload.get("api_key")
    except JWTError:
        raise_http_exception("Invalid JWT token", code=401)


def create_jwt(api_key: str):
    # Create JWT signature using the private key
    try:
        payload = {"api_key": api_key}
        token = jwt.encode(payload, private_key, algorithm=ALGORITHM)
        return token
    except Exception as e:
        raise_http_exception(f"Error generating JWT: {str(e)}")
