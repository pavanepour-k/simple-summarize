"""Services package initialization."""
from __future__ import annotations

from app.services.model_factory import register_model
from app.services.models.dummy import DummyModel
from app.services.models.huggingface import HuggingFaceModel

register_model("huggingface", HuggingFaceModel)
register_model("dummy", DummyModel)