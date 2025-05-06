from fastapi import APIRouter, UploadFile, File, Depends, Query, HTTPException, status
from app.models.request_model import SummaryOption, SummaryStyle, TextInput
from app.models.response_model import SummaryOutput
from app.services.summarizer import SummarizerService
from app.services.file_parser import extract_text_from_file, validate_file_type
from app.security.auth import verify_api_key, verify_user_access
from app.services.analytics import record_summary_usage

# User-specific router with API key authentication
user_router = APIRouter(
    dependencies=[Depends(verify_api_key)]
)

@user_router.post(
    "/text",
    response_model=SummaryOutput,
    summary="Summarize input text",
    description="Summarize the provided text based on selected options and style.",
    response_description="The summarized text with metadata like style and language.",
    status_code=200
)
async def summarize_text_input(
    data: TextInput,
    _: bool = Depends(verify_user_access),
    api_key: str = Depends(verify_api_key)
):
    summarizer = SummarizerService()
    return await _validate_and_summarize(data.content, data.option, data.style, api_key, summarizer)

@user_router.post(
    "/file",
    response_model=SummaryOutput,
    summary="Summarize uploaded file",
    description="Summarize the content of an uploaded file.",
    response_description="The summarized content extracted from the uploaded file.",
    status_code=200
)
async def summarize_uploaded_file(
    file: UploadFile = File(...),
    option: SummaryOption = Query(default=SummaryOption.medium),
    style: SummaryStyle = Query(default=SummaryStyle.general),
    _: bool = Depends(verify_user_access),
    api_key: str = Depends(verify_api_key)
):
    validate_file_type(file.filename)

    try:
        text = await extract_text_from_file(file)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to extract text from file: {str(e)}"
        )

    summarizer = SummarizerService()
    return await _validate_and_summarize(text, option, style, api_key, summarizer)

# Helper function for summarization logic
async def _validate_and_summarize(content: str, option: SummaryOption, style: SummaryStyle, api_key: str, summarizer: SummarizerService):
    try:
        # Detect language and apply summarization
        summary = await summarizer.summarize_async(content, option, style)
        
        # Record usage statistics
        await record_summary_usage(api_key, summary.language, summary.style)
        
        return summary
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Summarization error: {str(e)}"
        )