from __future__ import annotations

from fastapi import APIRouter, Depends, File, Query, UploadFile

from app.api.auth import verify_token
from app.models.file import FileUploadResponse
from app.models.summary import SummaryLength, SummaryResponse, SummaryStyle
from app.services.file_handler import FileHandlerService
from app.services.language import LanguageService
from app.services.statistics import StatisticsService
from app.services.summarizer import SummarizerService

router = APIRouter(prefix="/file", tags=["File"])


@router.post("/summarize", response_model=SummaryResponse)
async def summarize_file(
    file: UploadFile = File(...),
    style: SummaryStyle = Query(SummaryStyle.GENERAL),
    length: SummaryLength = Query(SummaryLength.MEDIUM),
    api_key: str = Depends(verify_token),
    file_handler: FileHandlerService = Depends(),
    summarizer: SummarizerService = Depends(),
    language_service: LanguageService = Depends(),
    stats: StatisticsService = Depends()
):
    text = await file_handler.extract_text(file)
    lang = language_service.detect_language(text)
    summary, used_lang = await summarizer.summarize(text, style, length, lang)
    
    await stats.record_usage(api_key, used_lang, style.value)
    
    return SummaryResponse(
        summary=summary,
        original_length=len(text),
        summary_length=len(summary),
        language=used_lang,
        style=style.value
    )


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    api_key: str = Depends(verify_token),
    file_handler: FileHandlerService = Depends()
):
    await file_handler.validate_file(file)
    text = await file_handler.extract_text(file)
    
    return FileUploadResponse(
        filename=file.filename,
        size=file.size,
        content_type=file.content_type,
        text_length=len(text)
    )