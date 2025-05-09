import os
import json
import logging
from functools import lru_cache
from typing import Dict, Any, Optional

# Import transformers conditionally - for actual production use
try:
    from transformers import pipeline, PreTrainedModel, PreTrainedTokenizer
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

from app.utils.error_handler import raise_http_exception

logger = logging.getLogger(__name__)

class ModelLoader:
    """
    Singleton class for loading and managing NLP models based on language.
    
    This class handles:
    - Loading model configurations from JSON
    - Caching loaded models in memory
    - Providing appropriate models for specific languages
    """
    _instance = None
    _models_config: Dict[str, str] = {}
    _model_cache = {}
    
    def __new__(cls):
        """Ensure singleton pattern - only one instance exists"""
        if cls._instance is None:
            cls._instance = super(ModelLoader, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize the model loader by loading configurations"""
        self._load_model_config()
    
    def _load_model_config(self):
        """Load model configuration from JSON file"""
        try:
            config_path = os.path.join("app", "config", "models.json")
            if os.path.exists(config_path):
                with open(config_path, 'r') as file:
                    self._models_config = json.load(file)
                logger.info(f"Loaded model configurations for {len(self._models_config)} languages")
            else:
                logger.warning(f"Model config file not found at {config_path}, using defaults")
                # Default fallback configuration
                self._models_config = {
                    "en": "facebook/bart-large-cnn",
                    "ko": "HeoAI/KoT5-summarization",
                    "ja": "line-corporation/line-distilbert-ja-summarization"
                }
        except Exception as e:
            logger.error(f"Failed to load model configurations: {str(e)}")
            # Default configuration as fallback
            self._models_config = {
                "en": "facebook/bart-large-cnn"
            }
    
    def get_model_path(self, lang: str) -> str:
        """
        Get the appropriate model path for a specific language.
        
        Args:
            lang (str): Language code (e.g., 'en', 'ko', 'ja')
            
        Returns:
            str: Model path for the specified language, or default model path for 'en'
        """
        model_path = self._models_config.get(lang.lower())
        if not model_path:
            logger.warning(f"No model configured for language '{lang}', using English model")
            model_path = self._models_config.get("en", "facebook/bart-large-cnn")
        return model_path
    
    @lru_cache(maxsize=8)  # Cache up to 8 different language models
    def get_pipeline(self, lang: str):
        """
        Get or create a summarization pipeline for the specified language.
        
        Args:
            lang (str): Language code (e.g., 'en', 'ko', 'ja')
            
        Returns:
            Pipeline: HuggingFace pipeline object for the specified language
            
        Raises:
            HTTPException: If loading the model fails or transformers is not available
        """
        if not TRANSFORMERS_AVAILABLE:
            logger.error("Transformers library not available for model loading")
            raise_http_exception(
                "Model loading service is currently unavailable", 
                code=503
            )
        
        lang = lang.lower()
        model_path = self.get_model_path(lang)
        
        try:
            if model_path not in self._model_cache:
                logger.info(f"Loading model for language '{lang}' from path '{model_path}'")
                # Create pipeline with device mapping based on availability
                self._model_cache[model_path] = pipeline(
                    "summarization", 
                    model=model_path,
                    device_map="auto"  # Use CUDA if available, otherwise CPU
                )
            return self._model_cache[model_path]
        except Exception as e:
            logger.error(f"Failed to load model for language '{lang}': {str(e)}")
            raise_http_exception(
                f"Failed to load summarization model: {str(e)}", 
                code=500
            )

    def get_supported_languages(self) -> list:
        """
        Return a list of all supported language codes.
        
        Returns:
            list: List of language codes supported by the system
        """
        return list(self._models_config.keys())


# Singleton instance for global use
def get_model_loader() -> ModelLoader:
    """
    Get the singleton instance of ModelLoader.
    
    Returns:
        ModelLoader: Singleton instance
    """
    return ModelLoader()