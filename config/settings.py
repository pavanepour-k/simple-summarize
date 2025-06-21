from __future__ import annotations

import logging
import sys
from enum import Enum
from pathlib import Path
from typing import List, Optional

from pydantic import Field, ValidationError, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class Environment(str, Enum):
    development = "development"
    production = "production"
    test = "test"


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    # General configuration
    API_NAME: str = "Simple Summarize API"
    ENV: Environment = Field(Environment.development, env="ENV")
    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")
    DEBUG_MODE: bool = Field(False, env="DEBUG_MODE")

    # Security keys
    API_KEY: str = Field(..., env="API_KEY")
    SECRET_KEY: str = Field(..., env="SECRET_KEY")

    # PII fields to redact (comma separated)
    PII_FIELDS: List[str] = Field(default_factory=list, env="PII_FIELDS")

    # Redis settings
    REDIS_HOST: str = Field(..., env="REDIS_HOST")
    REDIS_PORT: int = Field(..., env="REDIS_PORT")
    REDIS_DB: int = Field(..., env="REDIS_DB")
    REDIS_MAX_RETRIES: int = Field(3, env="REDIS_MAX_RETRIES")
    REDIS_MAX_CONNECTIONS: int = Field(10, env="REDIS_MAX_CONNECTIONS")

    # File upload settings
    MAX_FILE_SIZE_MB: int = Field(10, env="MAX_FILE_SIZE_MB")

    # Key file paths
    PRIVATE_KEY_PATH: Path = Field(..., env="PRIVATE_KEY_PATH")
    PUBLIC_KEY_PATH: Path = Field(..., env="PUBLIC_KEY_PATH")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    _private_key_cache: Optional[str] = None
    _public_key_cache: Optional[str] = None

    @field_validator("PII_FIELDS", mode="before")
    @classmethod
    def parse_pii_fields(cls, v):
        if isinstance(v, str):
            return [item.strip() for item in v.split(",") if item.strip()]
        return v

    @field_validator("MAX_FILE_SIZE_MB")
    @classmethod
    def check_max_file_size(cls, v):
        if v <= 0:
            raise ValueError("MAX_FILE_SIZE_MB must be greater than 0")
        return v

    @staticmethod
    def _read_key(path: Path, key_name: str) -> str:
        """Read a key file and raise ValueError if invalid."""
        if not path.is_file():
            raise ValueError(f"{key_name} file not found: {path}")
        text = path.read_text(encoding="utf-8").strip()
        if not text:
            raise ValueError(f"{key_name} file is empty: {path}")
        return text

    @property
    def PRIVATE_KEY(self) -> str:
        if self._private_key_cache is None:
            self._private_key_cache = self._read_key(self.PRIVATE_KEY_PATH, "Private key")
        return self._private_key_cache

    @property
    def PUBLIC_KEY(self) -> str:
        if self._public_key_cache is None:
            self._public_key_cache = self._read_key(self.PUBLIC_KEY_PATH, "Public key")
        return self._public_key_cache


def load_settings() -> Settings:
    try:
        settings = Settings()
        if not settings.API_KEY or not settings.SECRET_KEY:
            raise ValueError("Missing critical security keys (API_KEY / SECRET_KEY)")

        try:
            logging.getLogger().setLevel(settings.LOG_LEVEL.upper())
        except (ValueError, AttributeError):
            logger.warning("Invalid LOG_LEVEL %s, defaulting to INFO", settings.LOG_LEVEL)
            logging.getLogger().setLevel(logging.INFO)

        return settings
    except (ValidationError, ValueError) as exc:
        logger.error("Failed to load settings: %s", exc)
        sys.exit(1)


settings = load_settings()