"""Hugging Face transformers model implementation."""
from __future__ import annotations

import logging
from typing import Any, Dict, List

from transformers import pipeline

from app.services.base_model import BaseEmbeddingModel

logger = logging.getLogger(__name__)


class HuggingFaceModel(BaseEmbeddingModel):
    """Hugging Face transformers-based summarization model."""
    
    def __init__(self):
        self._pipeline = None
        self._model_name = None
        self._model_info = {}
    
    def load(self, model_path: str, **kwargs: Any) -> None:
        """Load Hugging Face model pipeline."""
        try:
            self._model_name = model_path
            self._pipeline = pipeline(
                "summarization",
                model=model_path,
                **kwargs
            )
            self._model_info = {
                "type": "huggingface",
                "model": model_path,
                "framework": "transformers"
            }
            logger.info(f"Loaded HuggingFace model: {model_path}")
        except Exception as e:
            logger.error(f"Failed to load model {model_path}: {e}")
            raise
    
    def summarize(
        self,
        text: str,
        max_length: int,
        min_length: int,
        **kwargs: Any
    ) -> List[Dict[str, str]]:
        """Generate summary using HuggingFace pipeline."""
        if not self._pipeline:
            raise RuntimeError("Model not loaded")
        
        result = self._pipeline(
            text,
            max_length=max_length,
            min_length=min_length,
            **kwargs
        )
        return result
    
    def get_info(self) -> Dict[str, Any]:
        """Get model information."""
        return self._model_info.copy()