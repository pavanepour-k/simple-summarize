"""Text summarization service."""
from __future__ import annotations

import asyncio
import functools
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple

from app.core.config import get_settings
from app.services.base_model import BaseEmbeddingModel
from app.services.model_factory import create_model
from app.utils.error_handler import InternalServerError

logger = logging.getLogger(__name__)


class SummaryStyle(str, Enum):
    GENERAL = "general"
    PROBLEM_SOLVING = "problem_solver"
    EMOTIONAL = "emotion_focused"


class SummaryOption(str, Enum):
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
    text: str
    language: str
    style_prompt: str


async def to_thread(func, *args, **kwargs):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, functools.partial(func, *args, **kwargs))


class SummarizerService:
    def __init__(self, model: Optional[BaseEmbeddingModel] = None):
        self._model = model
        self._settings = get_settings()
        
        if not self._model:
            self._model = create_model(
                model_type=self._settings.EMBEDDING_MODEL_TYPE,
                model_path=self._settings.EMBEDDING_MODEL_PATH,
                **self._settings.EMBEDDING_MODEL_PARAMS
            )
    
    async def summarize(
        self,
        text: str,
        language: str,
        style: SummaryStyle = SummaryStyle.GENERAL,
        option: SummaryOption = SummaryOption.MEDIUM
    ) -> Tuple[str, str, str]:
        return await to_thread(self._summarize_sync, text, language, style, option)
    
    async def summarize_with_meta(
        self,
        text: str,
        language: str,
        style: SummaryStyle = SummaryStyle.GENERAL,
        option: SummaryOption = SummaryOption.MEDIUM
    ) -> SummaryResult:
        text, lang, prompt = await self.summarize(text, language, style, option)
        return SummaryResult(text, lang, prompt)
    
    def _summarize_sync(
        self,
        text: str,
        language: str,
        style: SummaryStyle,
        option: SummaryOption
    ) -> Tuple[str, str, str]:
        try:
            style_prompt = STYLE_PROMPTS[style]
            length_params = LENGTH_PARAMS[option]
            
            input_text = f"{style_prompt} {text}"
            result = self._model.summarize(
                input_text,
                max_length=length_params["max_length"],
                min_length=length_params["min_length"]
            )
            
            return result[0]["summary_text"], language, style_prompt
            
        except Exception as e:
            logger.error(f"Summarization failed: {e}")
            raise InternalServerError(f"Failed to summarize text") from e