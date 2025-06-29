"""Dummy model for testing."""
from __future__ import annotations

from typing import Any, Dict, List

from app.services.base_model import BaseEmbeddingModel


class DummyModel(BaseEmbeddingModel):
    """Dummy model implementation for testing."""
    
    def __init__(self):
        self._loaded = False
        self._model_path = None
    
    def load(self, model_path: str, **kwargs: Any) -> None:
        self._model_path = model_path
        self._loaded = True
    
    def summarize(
        self,
        text: str,
        max_length: int,
        min_length: int,
        **kwargs: Any
    ) -> List[Dict[str, str]]:
        if not self._loaded:
            raise RuntimeError("Model not loaded")
        
        words = text.split()
        summary_length = min(max_length, max(min_length, len(words) // 4))
        summary = " ".join(words[:summary_length])
        
        return [{"summary_text": summary}]
    
    def get_info(self) -> Dict[str, Any]:
        return {
            "type": "dummy",
            "model": self._model_path,
            "loaded": self._loaded
        }