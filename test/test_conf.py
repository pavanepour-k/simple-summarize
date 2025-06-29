"""Test configuration and shared fixtures."""
from __future__ import annotations

import asyncio
import json
import os
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Generator, Optional
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import redis.asyncio as redis
from fastapi.testclient import TestClient
from jose import jwt

from app.core.config import Settings, get_settings
from app.main import app
from app.models.summary import SummaryLength, SummaryStyle
from app.models.user import UserRole
from app.services.base_model import BaseEmbeddingModel


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_settings() -> Settings:
    """Test-specific settings."""
    temp_dir = tempfile.mkdtemp()
    private_key_path = Path(temp_dir) / "private.pem"
    public_key_path = Path(temp_dir) / "public.pem"
    
    # Generate test RSA keys
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    public_key = private_key.public_key()
    
    private_key_path.write_bytes(
        private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
    )
    
    public_key_path.write_bytes(
        public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
    )
    
    return Settings(
        API_KEY="test-api-key",
        SECRET_KEY="test-secret-key",
        PRIVATE_KEY_PATH=private_key_path,
        PUBLIC_KEY_PATH=public_key_path,
        REDIS_URL="redis://localhost:6379/15",
        ENVIRONMENT="test",
        DEBUG=True,
        MAX_FILE_SIZE_MB=10,
        EMBEDDING_MODEL_TYPE="dummy",
        EMBEDDING_MODEL_PATH="test-model",
        RATE_LIMIT_PER_MINUTE=100
    )


@pytest.fixture
def mock_settings(test_settings: Settings, monkeypatch):
    """Mock application settings."""
    monkeypatch.setattr("app.core.config._settings", test_settings)
    monkeypatch.setattr("app.core.config.get_settings", lambda: test_settings)
    yield test_settings


@pytest.fixture
def client(mock_settings) -> TestClient:
    """FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def mock_redis():
    """Mock Redis client."""
    with patch("redis.asyncio.from_url") as mock_from_url:
        mock_client = AsyncMock(spec=redis.Redis)
        mock_from_url.return_value = mock_client
        
        # Mock common Redis operations
        mock_client.get = AsyncMock(return_value=None)
        mock_client.set = AsyncMock(return_value=True)
        mock_client.incr = AsyncMock(return_value=1)
        mock_client.lpush = AsyncMock(return_value=1)
        mock_client.lrange = AsyncMock(return_value=[])
        mock_client.keys = AsyncMock(return_value=[])
        mock_client.mget = AsyncMock(return_value=[])
        
        yield mock_client


@pytest.fixture
def mock_embedding_model():
    """Mock embedding model."""
    model = MagicMock(spec=BaseEmbeddingModel)
    model.summarize.return_value = [{
        "summary_text": "This is a test summary of the input text."
    }]
    model.get_info.return_value = {
        "type": "mock",
        "model": "test-model",
        "loaded": True
    }
    return model


@pytest.fixture
def auth_headers(test_settings: Settings) -> Dict[str, str]:
    """Valid authentication headers."""
    token = create_test_token(test_settings.API_KEY, UserRole.USER, test_settings)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_auth_headers(test_settings: Settings) -> Dict[str, str]:
    """Admin authentication headers."""
    token = create_test_token("admin_api_key", UserRole.ADMIN, test_settings)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_text_data() -> Dict[str, Any]:
    """Sample text summarization request data."""
    return {
        "content": "This is a long text that needs to be summarized. " * 50,
        "style": SummaryStyle.GENERAL.value,
        "length": SummaryLength.MEDIUM.value,
        "language": "en"
    }


@pytest.fixture
def sample_pdf_file():
    """Sample PDF file for testing."""
    import fitz  # PyMuPDF
    
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "This is a test PDF document with sample content.")
    
    pdf_bytes = doc.tobytes()
    doc.close()
    
    return ("test.pdf", pdf_bytes, "application/pdf")


@pytest.fixture
def sample_docx_file():
    """Sample DOCX file for testing."""
    from docx import Document
    
    doc = Document()
    doc.add_paragraph("This is a test DOCX document with sample content.")
    
    import io
    docx_bytes = io.BytesIO()
    doc.save(docx_bytes)
    docx_bytes.seek(0)
    
    return ("test.docx", docx_bytes.getvalue(), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")


@pytest.fixture
def sample_text_file():
    """Sample text file for testing."""
    content = b"This is a test text file with sample content."
    return ("test.txt", content, "text/plain")


@pytest.fixture
def large_file():
    """Large file exceeding size limit."""
    content = b"X" * (11 * 1024 * 1024)  # 11MB
    return ("large.txt", content, "text/plain")


def create_test_token(
    api_key: str,
    role: UserRole,
    settings: Settings,
    exp_minutes: int = 60
) -> str:
    """Create a test JWT token."""
    payload = {
        "api_key": api_key,
        "role": role.value,
        "exp": int((datetime.now(timezone.utc) + timedelta(minutes=exp_minutes)).timestamp())
    }
    return jwt.encode(payload, settings.PRIVATE_KEY, algorithm="RS256")


def create_expired_token(settings: Settings) -> str:
    """Create an expired JWT token."""
    return create_test_token(settings.API_KEY, UserRole.USER, settings, exp_minutes=-60)


def create_invalid_token() -> str:
    """Create an invalid JWT token."""
    return "invalid.jwt.token"


@pytest.fixture
def mock_summarizer_service(mock_embedding_model):
    """Mock summarizer service."""
    with patch("app.services.summarizer.create_model", return_value=mock_embedding_model):
        from app.services.summarizer import SummarizerService
        service = SummarizerService(model=mock_embedding_model)
        yield service


@pytest.fixture
def mock_file_handler():
    """Mock file handler service."""
    from app.services.file_handler import FileHandlerService
    
    handler = FileHandlerService()
    with patch.object(handler, "_extract_pdf", return_value="PDF content extracted"):
        with patch.object(handler, "_extract_docx", return_value="DOCX content extracted"):
            yield handler


@pytest.fixture
def mock_statistics_service(mock_redis):
    """Mock statistics service."""
    from app.services.statistics import StatisticsService
    
    service = StatisticsService()
    service._redis = mock_redis
    return service


@pytest.fixture
def mock_language_service():
    """Mock language service."""
    from app.services.language import LanguageService
    
    service = LanguageService()
    with patch.object(service, "detect_language", return_value="en"):
        yield service


@pytest.fixture(autouse=True)
def reset_singletons():
    """Reset singleton instances between tests."""
    from app.core import config
    config._settings = None
    yield
    config._settings = None


@pytest.fixture
def coverage_config():
    """Coverage configuration."""
    return {
        "source": ["app"],
        "omit": [
            "*/tests/*",
            "*/test_*",
            "*/__pycache__/*",
            "*/venv/*",
            "*/.venv/*"
        ],
        "branch": True,
        "parallel": True,
        "report": {
            "precision": 2,
            "show_missing": True,
            "skip_covered": False
        }
    }


class MockFileStorage:
    """Mock file storage for testing."""
    
    def __init__(self):
        self.files = {}
    
    async def save(self, filename: str, content: bytes) -> str:
        file_id = f"mock_{len(self.files)}"
        self.files[file_id] = {
            "filename": filename,
            "content": content,
            "timestamp": datetime.now(timezone.utc)
        }
        return file_id
    
    async def get(self, file_id: str) -> Optional[Dict[str, Any]]:
        return self.files.get(file_id)
    
    async def delete(self, file_id: str) -> bool:
        if file_id in self.files:
            del self.files[file_id]
            return True
        return False


@pytest.fixture
def mock_file_storage():
    """Mock file storage instance."""
    return MockFileStorage()


def generate_test_payloads() -> Dict[str, Any]:
    """Generate various test payloads."""
    return {
        "valid_summarization": {
            "content": "Test content for summarization",
            "style": "general",
            "length": "medium"
        },
        "invalid_style": {
            "content": "Test content",
            "style": "invalid_style",
            "length": "medium"
        },
        "missing_content": {
            "style": "general",
            "length": "medium"
        },
        "empty_content": {
            "content": "",
            "style": "general",
            "length": "medium"
        },
        "unicode_content": {
            "content": "Test with émojis 🚀 and unicode χαρακτήρες",
            "style": "general",
            "length": "short"
        }
    }


@pytest.fixture
def test_payloads():
    """Test payload factory."""
    return generate_test_payloads()


@pytest.fixture
def mock_time():
    """Mock time for consistent testing."""
    fixed_time = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    with patch("app.services.statistics.datetime") as mock_datetime:
        mock_datetime.utcnow.return_value = fixed_time
        mock_datetime.now.return_value = fixed_time
        yield fixed_time