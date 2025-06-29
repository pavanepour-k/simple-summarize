"""Configuration management."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings.
    
    Attributes:
        APP_NAME: Application name.
        VERSION: Application version.
        DEBUG: Debug mode flag.
        ENVIRONMENT: Deployment environment.
        API_KEY: API authentication key.
        SECRET_KEY: JWT secret key.
        PRIVATE_KEY_PATH: Path to private key file.
        PUBLIC_KEY_PATH: Path to public key file.
        REDIS_URL: Redis connection URL.
        REDIS_MAX_CONNECTIONS: Maximum Redis connections.
        MAX_FILE_SIZE_MB: Maximum upload file size.
        ALLOWED_EXTENSIONS: Allowed file extensions.
        DEFAULT_LANGUAGE: Default language code.
        SUPPORTED_LANGUAGES: Supported language codes.
        MODEL_CONFIG_PATH: Path to model configuration.
        LOG_LEVEL: Logging level.
        CORS_ORIGINS: Allowed CORS origins.
        RATE_LIMIT_PER_MINUTE: API rate limit.
    """
    
    APP_NAME: str = "Simple Summarize API"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = Field(default="production", pattern="^(development|production|test)$")
    
    API_KEY: str
    SECRET_KEY: str
    PRIVATE_KEY_PATH: Path
    PUBLIC_KEY_PATH: Path
    
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_MAX_CONNECTIONS: int = 10
    
    MAX_FILE_SIZE_MB: int = 10
    ALLOWED_EXTENSIONS: List[str] = [".pdf", ".docx", ".txt", ".md"]
    
    DEFAULT_LANGUAGE: str = "en"
    SUPPORTED_LANGUAGES: List[str] = ["en", "ko", "ja"]
    MODEL_CONFIG_PATH: Path = Path("app/config/models.json")
    
    LOG_LEVEL: str = "INFO"
    CORS_ORIGINS: List[str] = ["*"]
    RATE_LIMIT_PER_MINUTE: int = 60
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )

    EMBEDDING_MODEL_TYPE: str = "huggingface"
    EMBEDDING_MODEL_PATH: str = "facebook/bart-large-cnn"
    EMBEDDING_MODEL_PARAMS: Dict[str, Any] = {}
    
    _key_cache: Dict[str, str] = {}
    
    @field_validator("EMBEDDING_MODEL_TYPE")
    @classmethod
    def validate_model_type(cls, v: str) -> str:
        allowed = ["huggingface", "dummy"]
        if v not in allowed and "." not in v:
            raise ValueError(f"Model type must be one of {allowed} or a module path")
        return v

    @field_validator("MAX_FILE_SIZE_MB")
    @classmethod
    def validate_file_size(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("MAX_FILE_SIZE_MB must be positive")
        return v
    
    @field_validator("PRIVATE_KEY_PATH", "PUBLIC_KEY_PATH")
    @classmethod
    def validate_key_paths(cls, v: Path) -> Path:
        if not v.exists():
            raise ValueError(f"Key file not found: {v}")
        return v
    
    def load_key(self, key_type: str) -> str:
        if key_type not in self._key_cache:
            path = getattr(self, f"{key_type}_KEY_PATH")
            self._key_cache[key_type] = path.read_text().strip()
        return self._key_cache[key_type]
    
    @property
    def PRIVATE_KEY(self) -> str:
        return self.load_key("PRIVATE")
    
    @property
    def PUBLIC_KEY(self) -> str:
        return self.load_key("PUBLIC")


_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get application settings.
    
    Returns:
        Settings instance.
        
    Raises:
        SystemExit: If configuration is invalid.
    """
    global _settings
    if _settings is None:
        try:
            _settings = Settings()
        except Exception as e:
            print(f"Configuration error: {e}", file=sys.stderr)
            sys.exit(1)
    return _settings