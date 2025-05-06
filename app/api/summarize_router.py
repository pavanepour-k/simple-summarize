from fastapi import APIRouter, UploadFile, File, Depends, Query, HTTPException, status
from app.models.request_model import SummaryOption, SummaryStyle, TextInput
from app.models.response_model import SummaryOutput
<<<<<<< HEAD
from app.services.summarizer import SummarizerService  # SummarizerService 임포트
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
=======
from app.services.summarizer import SummarizerService
from app.services.file_parser import extract_text_from_file, validate_file_type
from app.security.auth import verify_api_key, verify_user_access
from app.services.analytics import record_summary_usage

# User-specific router with API key authentication
user_router = APIRouter(
    dependencies=[Depends(verify_api_key)]
)

>>>>>>> dev
@user_router.post(
    "/text",
    response_model=SummaryOutput,
    summary="Summarize input text",
    description="Summarize the provided text based on selected options and style.",
<<<<<<< HEAD
    response_description="The summarized text with additional metadata like style and language.",
=======
    response_description="The summarized text with metadata like style and language.",
>>>>>>> dev
    status_code=200
)
async def summarize_text_input(
    data: TextInput,
<<<<<<< HEAD
    _: bool = Depends(verify_user_access),  # 사용자 인증
    api_key: str = Depends(verify_api_key)
):
    summarizer = SummarizerService()  # SummarizerService 인스턴스화
    return await _validate_and_summarize(data.content, data.option, data.style, api_key, summarizer)

# 파일 업로드로 요약 처리
=======
    _: bool = Depends(verify_user_access),
    api_key: str = Depends(verify_api_key)
):
    summarizer = SummarizerService()
    return await _validate_and_summarize(data.content, data.option, data.style, api_key, summarizer)

>>>>>>> dev
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
<<<<<<< HEAD
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

    summarizer = SummarizerService()  # SummarizerService 인스턴스화
    return await _validate_and_summarize(text, option, style, api_key, summarizer)

# 관리자 전용 라우터에서만 접근 가능
@admin_router.get("/admin-stats", summary="관리자 전용 시스템 통계")
async def admin_stats():
    # 관리자 전용 통계 로직 (비동기 처리)
    return {"message": "관리자 전용 통계"}

# 텍스트 요약 수행을 위한 검증 및 요약 로직 (공통 함수)
async def _validate_and_summarize(content: str, option: SummaryOption, style: SummaryStyle, api_key: str, summarizer: SummarizerService):
    # 여기서는 API Key, 사용자 권한, 호출 한도 등을 검증하고 요약을 처리
    # 예시로 요약을 위한 기본 로직을 SummarizerService의 인스턴스를 사용하여 처리
    try:
        summary = summarizer.summarize(content, option, style)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"요약 중 오류 발생: {str(e)}")

    # 기록하기: 요약 사용에 대한 기록 (필요시)
    record_summary_usage(api_key)

    return summary
=======
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
>>>>>>> dev
