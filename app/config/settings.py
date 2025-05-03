from pydantic_settings import BaseSettings
from functools import lru_cache
from pydantic import Field  # 추가

class Settings(BaseSettings):
    API_NAME: str = "Simple Summarize API"
    DEBUG_MODE: bool = True
    API_ROLE: str = "user"  # 기본값 user, .env의 API_ROLE로 덮어쓰기
    API_KEY: str = Field(..., env="API_KEY")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"
        
@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
