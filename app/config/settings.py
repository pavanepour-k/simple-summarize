import os
from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class Settings(BaseSettings):
    # 기존 설정들
    API_NAME: str = "Simple Summarize API"
    DEBUG_MODE: bool = True
    API_ROLE: str = "user"
    API_KEY: str = Field(..., env="API_KEY")
    SECRET_KEY: str = Field(..., env="SECRET_KEY")

    # Redis 설정
    REDIS_HOST: str = Field(..., env="REDIS_HOST")
    REDIS_PORT: int = Field(..., env="REDIS_PORT")
    REDIS_DB: int = Field(..., env="REDIS_DB")
    REDIS_MAX_RETRIES: int = Field(..., env="REDIS_MAX_RETRIES")
    REDIS_MAX_CONNECTIONS: int = Field(..., env="REDIS_MAX_CONNECTIONS")
    
    MAX_FILE_SIZE_MB: int = Field(..., env="MAX_FILE_SIZE_MB")

    # PRIVATE_KEY_PATH 및 PUBLIC_KEY_PATH를 로드
    PRIVATE_KEY_PATH: str = Field(..., env="PRIVATE_KEY_PATH")
    PUBLIC_KEY_PATH: str = Field(..., env="PUBLIC_KEY_PATH")

    # ENVIRONMENT 설정 (기본값: "development")
    ENVIRONMENT: str = Field("development", env="ENVIRONMENT")  # 기본값을 "development"로 설정

    @property
    def PRIVATE_KEY(self):
        """PRIVATE_KEY_PATH에서 키를 읽어오는 메소드"""
        if os.path.exists(self.PRIVATE_KEY_PATH):
            with open(self.PRIVATE_KEY_PATH, 'r') as f:
                return f.read().strip()
        raise ValueError(f"Private key file not found at {self.PRIVATE_KEY_PATH}")

    @property
    def PUBLIC_KEY(self):
        """PUBLIC_KEY_PATH에서 키를 읽어오는 메소드"""
        if os.path.exists(self.PUBLIC_KEY_PATH):
            with open(self.PUBLIC_KEY_PATH, 'r') as f:
                return f.read().strip()
        raise ValueError(f"Public key file not found at {self.PUBLIC_KEY_PATH}")

    class Config:
        # .env 파일을 로드하여 환경 변수를 설정
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # 정의되지 않은 환경 변수 무시

# Settings 인스턴스 로드
def get_settings():
    try:
        return Settings()
    except Exception as e:
        print(f"Error loading settings: {e}")
        raise e

settings = get_settings()
