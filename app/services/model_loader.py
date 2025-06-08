import json
import logging
from transformers import pipeline
from functools import lru_cache
import os

# Initialize logger
logger = logging.getLogger(__name__)


class ModelLoader:
    # Singleton class to manage and cache language models

    _instance = None
    _model_config = None
    _selected_model_key = None    

    def __new__(cls, *args, **kwargs):
        # Ensure that only one instance of ModelLoader exists
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls._instance._load_model_config()  # Load model config when the first instance is created
        return cls._instance

    def _load_model_config(self):
        # Load model config from `models.json`
        try:
            # Use environment variables to set the config path
            config_path = os.getenv("MODEL_CONFIG_PATH", "config/models.json")
            with open(config_path, "r", encoding="utf-8") as f:
                self._model_config = json.load(f)

            # Read specific model key from environment variable
            self._selected_model_key = os.getenv("MODEL_NAME")
            if self._selected_model_key and self._selected_model_key not in self._model_config:
                logger.warning(
                    f"Model key '{self._selected_model_key}' not found in configuration."
                )
                self._selected_model_key = None

            logger.info("Successfully loaded model configuration.")
        except Exception as e:
            logger.error(f"Failed to load model configuration: {str(e)}")
            raise Exception("Failed to load model configuration.")

    @lru_cache(maxsize=None)
    def get_pipeline(self, lang: str):
        # Return the summarization pipeline for the requested language
        model_key = self._selected_model_key or lang
        model_name = self._model_config.get(model_key, self._model_config.get("en"))
        
        try:
            return pipeline("summarization", model=model_name)
        except Exception as e:
            logger.error(f"Failed to load model {model_name}: {str(e)}")
            fallback_model_name = self._model_config.get("en")
            logger.info(f"Falling back to default model: {fallback_model_name}")
            return pipeline(
                "summarization", model=fallback_model_name
            )  # Breaking long line for readability


# Create ModelLoader singleton instance
model_loader = ModelLoader()
