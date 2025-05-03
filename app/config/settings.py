from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    API_NAME: str = "Simple Summarize API"
    DEBUG_MODE: bool = True
    API_ROLE: str = "user"  # 기본값 user, .env의 API_ROLE로 덮어쓰기

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
