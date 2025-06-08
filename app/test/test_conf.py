import os
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from fastapi import APIRouter

# Stub out heavy summarizer router before importing app
sys.modules["app.api.summarize_router"] = type("m", (), {"user_router": APIRouter()})

# Create dummy key files for settings
for path in ("/tmp/private.pem", "/tmp/public.pem"):
    if not os.path.exists(path):
        with open(path, "w") as f:
            f.write("test")

# Required environment variables with dummy values
os.environ.setdefault("API_KEY", "test")
os.environ.setdefault("SECRET_KEY", "secret")
os.environ.setdefault("REDIS_HOST", "localhost")
os.environ.setdefault("REDIS_PORT", "6379")
os.environ.setdefault("REDIS_DB", "0")
os.environ.setdefault("REDIS_MAX_RETRIES", "1")
os.environ.setdefault("REDIS_MAX_CONNECTIONS", "1")
os.environ.setdefault("MAX_FILE_SIZE_MB", "10")
os.environ.setdefault("PRIVATE_KEY_PATH", "/tmp/private.pem")
os.environ.setdefault("PUBLIC_KEY_PATH", "/tmp/public.pem")
os.environ.setdefault("MODEL_CONFIG_PATH", "app/config/models.json")