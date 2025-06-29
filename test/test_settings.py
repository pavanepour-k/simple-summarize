import os
import tempfile
import pytest
from pathlib import Path
from config.settings import Settings, load_settings

# --- Fixture to create dummy key files ---
@pytest.fixture
def temp_keys():
    with tempfile.TemporaryDirectory() as temp_dir:
        private_key = Path(temp_dir) / "private.pem"
        public_key = Path(temp_dir) / "public.pem"
        private_key.write_text("PRIVATE_KEY_CONTENT")
        public_key.write_text("PUBLIC_KEY_CONTENT")
        yield private_key, public_key


def test_valid_env_and_log_level(temp_keys, monkeypatch):
    private_key, public_key = temp_keys
    monkeypatch.setenv("ENV", "development")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("API_KEY", "abc")
    monkeypatch.setenv("SECRET_KEY", "xyz")
    monkeypatch.setenv("PII_FIELDS", "name, email ")
    monkeypatch.setenv("PRIVATE_KEY_PATH", str(private_key))
    monkeypatch.setenv("PUBLIC_KEY_PATH", str(public_key))
    monkeypatch.setenv("REDIS_HOST", "localhost")
    monkeypatch.setenv("REDIS_PORT", "6379")
    monkeypatch.setenv("REDIS_DB", "0")
    monkeypatch.setenv("REDIS_MAX_RETRIES", "3")
    monkeypatch.setenv("REDIS_MAX_CONNECTIONS", "10")
    monkeypatch.setenv("MAX_FILE_SIZE_MB", "5")

    settings = load_settings()
    assert settings.ENV == "development"
    assert settings.LOG_LEVEL == "DEBUG"
    assert settings.PII_FIELDS == ["name", "email"]
    assert settings.PRIVATE_KEY == "PRIVATE_KEY_CONTENT"
    assert settings.PUBLIC_KEY == "PUBLIC_KEY_CONTENT"


def test_invalid_log_level_fallback(temp_keys, monkeypatch, caplog):
    private_key, public_key = temp_keys
    monkeypatch.setenv("LOG_LEVEL", "INVALID")
    monkeypatch.setenv("API_KEY", "abc")
    monkeypatch.setenv("SECRET_KEY", "xyz")
    monkeypatch.setenv("PRIVATE_KEY_PATH", str(private_key))
    monkeypatch.setenv("PUBLIC_KEY_PATH", str(public_key))
    monkeypatch.setenv("ENV", "test")
    monkeypatch.setenv("REDIS_HOST", "localhost")
    monkeypatch.setenv("REDIS_PORT", "6379")
    monkeypatch.setenv("REDIS_DB", "0")
    monkeypatch.setenv("REDIS_MAX_RETRIES", "3")
    monkeypatch.setenv("REDIS_MAX_CONNECTIONS", "10")
    monkeypatch.setenv("MAX_FILE_SIZE_MB", "5")

    with caplog.at_level("WARNING"):
        settings = load_settings()
        assert "Invalid LOG_LEVEL" in caplog.text


def test_missing_key_file(monkeypatch):
    monkeypatch.setenv("API_KEY", "abc")
    monkeypatch.setenv("SECRET_KEY", "xyz")
    monkeypatch.setenv("PRIVATE_KEY_PATH", "/invalid/private.pem")
    monkeypatch.setenv("PUBLIC_KEY_PATH", "/invalid/public.pem")
    monkeypatch.setenv("ENV", "production")
    monkeypatch.setenv("REDIS_HOST", "localhost")
    monkeypatch.setenv("REDIS_PORT", "6379")
    monkeypatch.setenv("REDIS_DB", "0")
    monkeypatch.setenv("REDIS_MAX_RETRIES", "3")
    monkeypatch.setenv("REDIS_MAX_CONNECTIONS", "10")
    monkeypatch.setenv("MAX_FILE_SIZE_MB", "5")

    with pytest.raises(SystemExit):
        load_settings()


def test_zero_max_file_size(temp_keys, monkeypatch):
    private_key, public_key = temp_keys
    monkeypatch.setenv("MAX_FILE_SIZE_MB", "0")
    monkeypatch.setenv("API_KEY", "abc")
    monkeypatch.setenv("SECRET_KEY", "xyz")
    monkeypatch.setenv("PRIVATE_KEY_PATH", str(private_key))
    monkeypatch.setenv("PUBLIC_KEY_PATH", str(public_key))
    monkeypatch.setenv("ENV", "production")
    monkeypatch.setenv("REDIS_HOST", "localhost")
    monkeypatch.setenv("REDIS_PORT", "6379")
    monkeypatch.setenv("REDIS_DB", "0")
    monkeypatch.setenv("REDIS_MAX_RETRIES", "3")
    monkeypatch.setenv("REDIS_MAX_CONNECTIONS", "10")

    with pytest.raises(SystemExit):
        load_settings()
