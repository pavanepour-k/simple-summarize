"""Text summarization service."""
from __future__ import annotations

import asyncio
import functools
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple

from app.services.model_loader import ModelLoader
from app.utils.error_handler import InternalServerError

logger = logging.getLogger(__name__)


class SummaryStyle(str, Enum):
    """Summarization style options."""
    
    GENERAL = "general"
    PROBLEM_SOLVING = "problem_solver"
    EMOTIONAL = "emotion_focused"


class SummaryOption(str, Enum):
    """Summary length options."""
    
    SHORT = "short"
    MEDIUM = "medium"
    LONG = "long"


STYLE_PROMPTS = {
    SummaryStyle.GENERAL: "Summarize this text in a neutral and concise manner.",
    SummaryStyle.PROBLEM_SOLVING: "Summarize this text, focusing on the solution and problem-solving aspects.",
    SummaryStyle.EMOTIONAL: "Summarize this text with an emotional tone, capturing the feelings and emotions expressed."
}

LENGTH_PARAMS = {
    SummaryOption.SHORT: {"max_length": 50, "min_length": 25},
    SummaryOption.MEDIUM: {"max_length": 150, "min_length": 80},
    SummaryOption.LONG: {"max_length": 300, "min_length": 150}
}


@dataclass
class SummaryResult:
    """Summary result with metadata."""
    
    text: str
    language: str
    style_prompt: str


async def to_thread(func, *args, **kwargs):
    """Run function in thread pool."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, functools.partial(func, *args, **kwargs))


class SummarizerService:
    """Text summarization service."""
    
    def __init__(self, model_loader: Optional[ModelLoader] = None):
        self._model_loader = model_loader or ModelLoader()
    
    async def summarize(
        self,
        text: str,
        language: str,
        style: SummaryStyle = SummaryStyle.GENERAL,
        option: SummaryOption = SummaryOption.MEDIUM
    ) -> Tuple[str, str, str]:
        """Summarize text.
        
        Args:
            text: Input text
            language: Language code
            style: Summary style
            option: Summary length
            
        Returns:
            Tuple of (summary_text, language, style_prompt)
            
        Raises:
            InternalServerError: If summarization fails
        """
        return await to_thread(self._summarize_sync, text, language, style, option)
    
    async def summarize_with_meta(
        self,
        text: str,
        language: str,
        style: SummaryStyle = SummaryStyle.GENERAL,
        option: SummaryOption = SummaryOption.MEDIUM
    ) -> SummaryResult:
        """Summarize text with metadata.
        
        Args:
            text: Input text
            language: Language code
            style: Summary style
            option: Summary length
            
        Returns:
            SummaryResult with text and metadata
        """
        text, lang, prompt = await self.summarize(text, language, style, option)
        return SummaryResult(text, lang, prompt)
    
    def _summarize_sync(
        self,
        text: str,
        language: str,
        style: SummaryStyle,
        option: SummaryOption
    ) -> Tuple[str, str, str]:
        """Synchronous summarization implementation."""
        try:
            style_prompt = STYLE_PROMPTS[style]
            length_params = LENGTH_PARAMS[option]
            
            try:
                pipeline = self._model_loader.get_pipeline(language)
            except Exception:
                logger.error(f"Failed to load {language} model, using English")
                pipeline = self._model_loader.get_pipeline("en")
                language = "en"
            
            input_text = f"{style_prompt} {text}"
            result = pipeline(
                input_text,
                max_length=length_params["max_length"],
                min_length=length_params["min_length"]
            )
            
            return result[0]["summary_text"], language, style_prompt
            
        except Exception as e:
            logger.error(f"Summarization failed: {e}")
            raise InternalServerError(f"Failed to summarize text") from e