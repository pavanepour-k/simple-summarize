from pydantic_settings import BaseSettings
from functools import lru_cache
from pydantic import Field  # 추가

class Settings(BaseSettings):
    # API와 관련된 설정 값들
    API_NAME: str = "Simple Summarize API"
    DEBUG_MODE: bool = True
    API_ROLE: str = "user"  # 기본값 user, .env의 API_ROLE로 덮어쓰기
    API_KEY: str = Field(..., env="API_KEY")  # .env에서 로드할 API_KEY
    
    # Redis 관련 설정 (필요한 경우 추가)
    REDIS_HOST: str = Field(..., env="REDIS_HOST")
    REDIS_PORT: int = Field(..., env="REDIS_PORT")
    REDIS_DB: int = Field(..., env="REDIS_DB")
    REDIS_MAX_RETRIES: int = Field(..., env="REDIS_MAX_RETRIES")
    REDIS_MAX_CONNECTIONS: int = Field(..., env="REDIS_MAX_CONNECTIONS")

    MAX_FILE_SIZE_MB: int = Field(..., env="MAX_FILE_SIZE_MB")

    class Config:
        # .env 파일을 로드하여 환경 변수를 설정
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # 정의되지 않은 환경 변수 무시

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
