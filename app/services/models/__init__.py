"""Model implementations."""
from __future__ import annotations

from app.services.models.dummy import DummyModel
from app.services.models.huggingface import HuggingFaceModel

__all__ = ["HuggingFaceModel", "DummyModel"]