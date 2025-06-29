"""Base embedding model interface."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple


class BaseEmbeddingModel(ABC):
    """Abstract base class for embedding models."""
    
    @abstractmethod
    def load(self, model_path: str, **kwargs: Any) -> None:
        """Load model from path.
        
        Args:
            model_path: Path to model files
            **kwargs: Additional model-specific parameters
        """
        pass
    
    @abstractmethod
    def summarize(
        self,
        text: str,
        max_length: int,
        min_length: int,
        **kwargs: Any
    ) -> List[Dict[str, str]]:
        """Generate summary for input text.
        
        Args:
            text: Input text to summarize
            max_length: Maximum summary length
            min_length: Minimum summary length
            **kwargs: Additional model-specific parameters
            
        Returns:
            List of summary dictionaries with 'summary_text' key
        """
        pass
    
    @abstractmethod
    def get_info(self) -> Dict[str, Any]:
        """Get model information.
        
        Returns:
            Dictionary with model metadata
        """
        pass