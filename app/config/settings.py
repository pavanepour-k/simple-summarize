from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    API_NAME: str = "Simple Summarize API"
    DEBUG_MODE: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
