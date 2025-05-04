from fastapi import APIRouter, UploadFile, File, Depends, Query, HTTPException, status
from app.models.request_model import SummaryOption, SummaryStyle, TextInput
from app.models.response_model import SummaryOutput
from app.services.summarizer import summarize_text, detect_language
from app.services.file_parser import extract_text_from_file
from app.security.auth import verify_api_key, verify_user_access, verify_admin
from app.security.user_roles import get_user_role
from app.services.analytics import record_summary_usage, get_usage_stats, get_recent_logs

# 사용자 전용 라우터
user_router = APIRouter(
    dependencies=[Depends(verify_api_key)]  # API 키 인증
)

# 관리자 전용 라우터를 별도로 분리
admin_router = APIRouter(
    dependencies=[Depends(verify_admin)]  # 관리자 권한 확인
)

# 사용자가 요청한 텍스트 요약
@user_router.post(
    "/text",
    response_model=SummaryOutput,
    summary="Summarize input text",
    description="Summarize the provided text based on selected options and style.",
    response_description="The summarized text with additional metadata like style and language.",
    status_code=200
)
async def summarize_text_input(
    data: TextInput,
    _: bool = Depends(verify_user_access),  # 사용자 인증
    api_key: str = Depends(verify_api_key)
):
    return await _validate_and_summarize(data.content, data.option, data.style, api_key)

# 파일 업로드로 요약 처리
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
    _: bool = Depends(verify_user_access),  # 사용자 인증
    api_key: str = Depends(verify_api_key)
):
    _validate_file_type(file.filename)

    try:
        text = await extract_text_from_file(file)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="파일에서 텍스트를 추출하는 데 실패했습니다. 파일이 손상되었거나 형식이 잘못되었을 수 있습니다."
        )

    return await _validate_and_summarize(text, option, style, api_key)

# 관리자 전용 라우터에서만 접근 가능
@admin_router.get("/admin-stats", summary="관리자 전용 시스템 통계")
async def admin_stats():
    # 관리자 전용 통계 로직 (비동기 처리)
    return {"message": "관리자 전용 통계"}
