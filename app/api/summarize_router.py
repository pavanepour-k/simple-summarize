from fastapi import APIRouter, UploadFile, File, Depends, Query
from app.models.request_model import SummaryOption, SummaryStyle, TextInput
from app.models.response_model import SummaryOutput
from app.services.summarizer import summarize_text, detect_language
from app.services.file_parser import extract_text_from_file
from app.security.auth import verify_api_key, verify_user_access, verify_admin

router = APIRouter(dependencies=[Depends(verify_api_key)])

async def _validate_and_summarize(
    content: str, 
    option: SummaryOption, 
    style: SummaryStyle, 
    api_key: str
) -> SummaryOutput:
    if style != SummaryStyle.general:
        verify_admin(api_key)
    
    lang = detect_language(content)
    result = summarize_text(content, option, style, lang)
    return result

@router.post(
    "/text",
    response_model=SummaryOutput,
    summary="Summarize input text",
    description="Summarize the provided text based on selected options and style.",
    response_description="The summarized text with additional metadata like style and language.",
    status_code=200,
    examples={
        "application/json": {
            "summary": "Summarized content here",
            "length": "medium",
            "input_length": 1000,
            "language": "en",
            "style": "general",
            "style_prompt": "Summarize the content in a general manner."
        }
    }
)
async def summarize_text_input(
    data: TextInput,
    _: bool = Depends(verify_user_access),
    api_key: str = Depends(verify_api_key)
):
    result = await _validate_and_summarize(data.content, data.option, data.style, api_key)
    return result

@router.post(
    "/file",
    response_model=SummaryOutput,
    summary="Summarize uploaded file",
    description="Summarize the content of an uploaded file.",
    response_description="The summarized content extracted from the uploaded file.",
    status_code=200,
    examples={
        "application/json": {
            "summary": "Summarized content from file",
            "length": "long",
            "input_length": 1500,
            "language": "en",
            "style": "problem_solver",
            "style_prompt": "Summarize the content by focusing on identifying problems and solutions."
        }
    }
)
async def summarize_uploaded_file(
    file: UploadFile = File(...),
    option: SummaryOption = Query(default=SummaryOption.medium),
    style: SummaryStyle = Query(default=SummaryStyle.general),
    _: bool = Depends(verify_user_access),
    api_key: str = Depends(verify_api_key)
):
    text = await extract_text_from_file(file)
    result = await _validate_and_summarize(text, option, style, api_key)
    return result
