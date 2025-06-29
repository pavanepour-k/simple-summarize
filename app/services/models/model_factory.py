"""Model factory for creating embedding model instances."""
from __future__ import annotations

import importlib
import logging
from typing import Any, Dict, Type

from app.services.base_model import BaseEmbeddingModel

logger = logging.getLogger(__name__)

_MODEL_REGISTRY: Dict[str, Type[BaseEmbeddingModel]] = {}


def register_model(name: str, model_class: Type[BaseEmbeddingModel]) -> None:
    _MODEL_REGISTRY[name] = model_class


def create_model(
    model_type: str,
    model_path: str,
    **kwargs: Any
) -> BaseEmbeddingModel:
    if model_type not in _MODEL_REGISTRY:
        try:
            module_path, class_name = model_type.rsplit(".", 1)
            module = importlib.import_module(module_path)
            model_class = getattr(module, class_name)
            register_model(model_type, model_class)
        except Exception as e:
            logger.error(f"Failed to import model {model_type}: {e}")
            raise ValueError(f"Unknown model type: {model_type}")
    
    model_class = _MODEL_REGISTRY[model_type]
    model = model_class()
    model.load(model_path, **kwargs)
    return model