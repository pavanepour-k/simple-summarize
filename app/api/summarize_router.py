from fastapi import APIRouter, UploadFile, File, Depends, Query, HTTPException
from app.models.request_model import SummaryOption, SummaryStyle, TextInput
from app.models.response_model import SummaryOutput
from app.services.summarizer import summarize_text
from app.services.file_parser import extract_text_from_file
from app.security.auth import verify_api_key, is_admin

# 모든 라우트에 API Key 인증 적용
router = APIRouter(
    dependencies=[Depends(verify_api_key)]
)

@router.post(
    "/text",
    response_model=SummaryOutput,
    summary="Summarize input text",
    description="Summarize the provided text based on the selected option (short, medium, long) and style."
)
async def summarize_text_input(data: TextInput):
    # 고급 스타일은 관리자만 사용 가능
    if data.style != SummaryStyle.general and not is_admin():
        raise HTTPException(
            status_code=403,
            detail={"error": "Only admin users can use advanced summary styles."}
        )

    result = summarize_text(data.content, data.option, data.style)
    return result

@router.post(
    "/file",
    response_model=SummaryOutput,
    summary="Summarize uploaded file",
    description="Summarize the content of a PDF or DOCX file based on the selected option and style."
)
async def summarize_uploaded_file(
    file: UploadFile = File(...),
    option: SummaryOption = Query(
        default=SummaryOption.medium,
        description="Summary length option"
    ),
    style: SummaryStyle = Query(
        default=SummaryStyle.general,
        description="Choose a summary style: general (default), problem_solver, or emotion_focused."
    ),
):
    # 고급 스타일은 관리자만 사용 가능
    if style != SummaryStyle.general and not is_admin():
        raise HTTPException(
            status_code=403,
            detail={"error": "Only admin users can use advanced summary styles."}
        )

    # 파일 파싱
    text = await extract_text_from_file(file)
    # 요약 수행
    result = summarize_text(text, option, style)
    return result
