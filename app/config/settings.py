import os
from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv

# Load .env file
load_dotenv()


class Settings(BaseSettings):
    # Configuration settings
    API_NAME: str = "Simple Summarize API"
    DEBUG_MODE: bool = True
    API_ROLE: str = "user"
    API_KEY: str = Field(..., env="API_KEY")
    SECRET_KEY: str = Field(..., env="SECRET_KEY")

    # Redis settings
    REDIS_HOST: str = Field(..., env="REDIS_HOST")
    REDIS_PORT: int = Field(..., env="REDIS_PORT")
    REDIS_DB: int = Field(..., env="REDIS_DB")
    REDIS_MAX_RETRIES: int = Field(..., env="REDIS_MAX_RETRIES")
    REDIS_MAX_CONNECTIONS: int = Field(..., env="REDIS_MAX_CONNECTIONS")
    
    MAX_FILE_SIZE_MB: int = Field(..., env="MAX_FILE_SIZE_MB")

    # Load PRIVATE_KEY_PATH and PUBLIC_KEY_PATH
    PRIVATE_KEY_PATH: str = Field(..., env="PRIVATE_KEY_PATH")
    PUBLIC_KEY_PATH: str = Field(..., env="PUBLIC_KEY_PATH")

    # ENVIRONMENT setting (default: "development")
    ENVIRONMENT: str = Field(
        "development", env="ENVIRONMENT"
    )  # Default is "development"

    _private_key_cache: str | None = None
    _public_key_cache: str | None = None

    def PRIVATE_KEY(self) -> str:
        """Return the loaded private key.

        The key is read once from ``PRIVATE_KEY_PATH`` and cached for subsequent
        calls. A ``ValueError`` is raised if the file does not exist or is empty.
        """
        if self._private_key_cache is None:
            if not os.path.isfile(self.PRIVATE_KEY_PATH):
                raise ValueError(
                    f"Private key file not found at {self.PRIVATE_KEY_PATH}"
                )
            with open(self.PRIVATE_KEY_PATH, "r", encoding="utf-8") as f:
                self._private_key_cache = f.read().strip()
            if not self._private_key_cache:
                raise ValueError("Private key file is empty")
        return self._private_key_cache

    @property
    def PUBLIC_KEY(self) -> str:
        """Return the loaded public key.

        The key is loaded from ``PUBLIC_KEY_PATH`` only once. A ``ValueError``
        is raised if the file is missing or empty.
        """
        if self._public_key_cache is None:
            if not os.path.isfile(self.PUBLIC_KEY_PATH):
                raise ValueError(
                    f"Public key file not found at {self.PUBLIC_KEY_PATH}"
                )
            with open(self.PUBLIC_KEY_PATH, "r", encoding="utf-8") as f:
                self._public_key_cache = f.read().strip()
            if not self._public_key_cache:
                raise ValueError("Public key file is empty")
        return self._public_key_cache

    class Config:
        # Load environment variables from the .env file
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Ignore undefined environment variables


# Load the Settings instance
def get_settings():
    try:
        return Settings()
    except Exception as e:
        print(f"Error loading settings: {e}")
        raise e


settings = get_settings()
