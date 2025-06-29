"""Model loading service."""
from __future__ import annotations

import json
import logging
import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Optional

from app.utils.error_handler import InternalServerError

logger = logging.getLogger(__name__)


class ModelLoader:
    """Language model loader with caching."""
    
    def __init__(self, config_path: Optional[str] = None):
        self._config_path = config_path or os.getenv(
            "MODEL_CONFIG_PATH", "app/config/models.json"
        )
        self._model_config = self._load_config()
        self._selected_model = os.getenv("MODEL_NAME")
    
    def _load_config(self) -> Dict[str, str]:
        """Load model configuration."""
        try:
            path = Path(self._config_path)
            if not path.exists():
                logger.error(f"Model config not found: {path}")
                return {"en": "facebook/bart-large-cnn"}
            
            with path.open("r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load model config: {e}")
            return {"en": "facebook/bart-large-cnn"}
    
    @lru_cache(maxsize=None)
    def get_pipeline(self, language: str) -> Any:
        """Get model pipeline for language.
        
        Args:
            language: Language code
            
        Returns:
            Model pipeline
            
        Raises:
            InternalServerError: If model loading fails
        """
        model_key = self._selected_model or language
        model_name = self._model_config.get(
            model_key, self._model_config.get("en")
        )
        
        try:
            return self._load_model(model_name)
        except Exception as e:
            logger.error(f"Failed to load {model_name}: {e}")
            if model_key != "en":
                logger.info("Falling back to English model")
                return self._load_model(self._model_config["en"])
            raise InternalServerError("Failed to load model") from e
    
    def _load_model(self, model_name: str) -> Any:
        """Load model implementation."""
        from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, pipeline
        
        try:
            model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            return pipeline("summarization", model=model, tokenizer=tokenizer)
        except Exception as e:
            logger.error(f"Model loading failed: {e}")
            raise