from __future__ import annotations

from langdetect import detect

from app.core.config import get_settings


class LanguageService:
    def detect_language(self, text: str) -> str:
        try:
            lang = detect(text)
            settings = get_settings()
            return lang if lang in settings.SUPPORTED_LANGUAGES else settings.DEFAULT_LANGUAGE
        except:
            return get_settings().DEFAULT_LANGUAGE