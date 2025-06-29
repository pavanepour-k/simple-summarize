"""Application settings configuration."""
from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application configuration loaded from environment variables.
    
    Attributes:
        API_NAME: Name of the API service
        DEBUG_MODE: Enable debug mode
        API_KEY: API authentication key
        SECRET_KEY: Secret key for JWT
        REDIS_HOST: Redis server hostname
        REDIS_PORT: Redis server port
        REDIS_DB: Redis database number
        REDIS_MAX_RETRIES: Maximum retry attempts for Redis
        REDIS_MAX_CONNECTIONS: Maximum Redis connections
        MAX_FILE_SIZE_MB: Maximum file upload size in MB
        PRIVATE_KEY_PATH: Path to private key file
        PUBLIC_KEY_PATH: Path to public key file
        ENVIRONMENT: Deployment environment
    """
    
    API_NAME: str = Field(default="Simple Summarize API")
    DEBUG_MODE: bool = Field(default=False)
    API_KEY: str = Field(...)
    SECRET_KEY: str = Field(...)
    
    REDIS_HOST: str = Field(...)
    REDIS_PORT: int = Field(...)
    REDIS_DB: int = Field(...)
    REDIS_MAX_RETRIES: int = Field(default=3)
    REDIS_MAX_CONNECTIONS: int = Field(default=10)
    
    MAX_FILE_SIZE_MB: int = Field(default=10)
    
    PRIVATE_KEY_PATH: Path = Field(...)
    PUBLIC_KEY_PATH: Path = Field(...)
    
    ENVIRONMENT: str = Field(default="development")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    _private_key_cache: Optional[str] = None
    _public_key_cache: Optional[str] = None
    
    @field_validator("MAX_FILE_SIZE_MB")
    @classmethod
    def validate_file_size(cls, v: int) -> int:
        """Validate maximum file size.
        
        Args:
            v: File size in MB
            
        Returns:
            Validated file size
            
        Raises:
            ValueError: If file size is invalid
        """
        if v <= 0:
            raise ValueError("MAX_FILE_SIZE_MB must be greater than 0")
        return v
    
    @property
    def PRIVATE_KEY(self) -> str:
        """Load and cache private key.
        
        Returns:
            Private key content
            
        Raises:
            ValueError: If key file not found or empty
        """
        if self._private_key_cache is None:
            self._private_key_cache = self._read_key_file(
                self.PRIVATE_KEY_PATH, "Private key"
            )
        return self._private_key_cache
    
    @property
    def PUBLIC_KEY(self) -> str:
        """Load and cache public key.
        
        Returns:
            Public key content
            
        Raises:
            ValueError: If key file not found or empty
        """
        if self._public_key_cache is None:
            self._public_key_cache = self._read_key_file(
                self.PUBLIC_KEY_PATH, "Public key"
            )
        return self._public_key_cache
    
    def _read_key_file(self, path: Path, key_type: str) -> str:
        """Read key file content.
        
        Args:
            path: Path to key file
            key_type: Type of key for error messages
            
        Returns:
            Key file content
            
        Raises:
            ValueError: If file not found or empty
        """
        if not path.is_file():
            raise ValueError(f"{key_type} file not found at {path}")
        
        content = path.read_text(encoding="utf-8").strip()
        if not content:
            raise ValueError(f"{key_type} file is empty")
        
        return content


def get_settings() -> Settings:
    """Load and validate application settings.
    
    Returns:
        Validated settings instance
        
    Raises:
        SystemExit: If settings validation fails
    """
    try:
        return Settings()
    except Exception as e:
        logger.error(f"Failed to load settings: {e}")
        raise SystemExit(1) from e


# Module-level instance for backwards compatibility
# Should be accessed through get_settings() in new code
settings = get_settings()