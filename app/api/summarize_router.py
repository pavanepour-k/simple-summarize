from fastapi import APIRouter, UploadFile, File, Depends, Query
from app.models.request_model import TextInput, SummaryOption
from app.models.response_model import SummaryOutput
from app.services.summarizer import summarize_text
from app.services.file_parser import extract_text_from_file
from app.security.auth import verify_api_key

# 모든 라우트에 API Key 인증 적용
router = APIRouter(
    dependencies=[Depends(verify_api_key)]
)

@router.post(
    "/text",
    response_model=SummaryOutput,
    summary="Summarize input text",
    description="Summarize the provided text based on the selected option (short, medium, long)."
)
async def summarize_text_input(data: TextInput):
    result = summarize_text(data.content, data.option)
    return result

@router.post(
    "/file",
    response_model=SummaryOutput,
    summary="Summarize uploaded file",
    description="Summarize the content of a PDF or DOCX file based on the selected option."
)
async def summarize_uploaded_file(
    file: UploadFile = File(...),
    option: SummaryOption = Query(default=SummaryOption.medium, description="Summary length option"),
):
    text = await extract_text_from_file(file)
    result = summarize_text(text, option)
    return result
