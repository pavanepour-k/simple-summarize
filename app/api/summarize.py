from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.auth import verify_token
from app.models.summary import SummaryRequest, SummaryResponse
from app.services.language import LanguageService
from app.services.statistics import StatisticsService
from app.services.summarizer import SummarizerService

router = APIRouter(prefix="/summarize", tags=["Summarization"])


@router.post("/text", response_model=SummaryResponse)
async def summarize_text(
    request: SummaryRequest,
    api_key: str = Depends(verify_token),
    summarizer: SummarizerService = Depends(),
    language_service: LanguageService = Depends(),
    stats: StatisticsService = Depends()
):
    lang = request.language or language_service.detect_language(request.content)
    summary, used_lang = await summarizer.summarize(
        request.content, request.style, request.length, lang
    )
    
    await stats.record_usage(api_key, used_lang, request.style.value)
    
    return SummaryResponse(
        summary=summary,
        original_length=len(request.content),
        summary_length=len(summary),
        language=used_lang,
        style=request.style.value
    )