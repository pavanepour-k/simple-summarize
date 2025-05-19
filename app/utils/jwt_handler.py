from jose import JWTError, jwt
from app.config.settings import settings  # settings에서 공개 키와 비밀 키 사용
from app.utils.error_handler import raise_http_exception
from cryptography.hazmat.primitives import serialization

# 공개 키와 비밀 키 로드
private_key = settings.PRIVATE_KEY
public_key = settings.PUBLIC_KEY  # PUBLIC_KEY를 settings에서 로드

ALGORITHM = "RS256"

def verify_jwt(token: str):
    try:
        # 공개 키를 사용하여 JWT를 검증
        payload = jwt.decode(token, public_key, algorithms=[ALGORITHM])
        return payload.get("api_key")
    except JWTError:
        raise_http_exception("Invalid JWT token", code=401)

def create_jwt(api_key: str):
    try:
        # 개인 키를 사용하여 JWT 서명 생성
        payload = {"api_key": api_key}
        token = jwt.encode(payload, private_key, algorithm=ALGORITHM)
        return token
    except Exception as e:
        raise_http_exception(f"Error generating JWT: {str(e)}")
