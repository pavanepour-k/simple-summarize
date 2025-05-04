from fastapi import APIRouter, Depends
from app.security.auth import verify_admin
from app.services.analytics import get_usage_stats, get_recent_logs

# 관리자 전용 라우터
admin_router = APIRouter(
    prefix="/admin", 
    tags=["Admin"], 
    dependencies=[Depends(verify_admin)]  # 모든 관리자 전용 API에 대한 인증 적용
)

@admin_router.get("/stats", summary="시스템 통계 조회", description="요약 API 사용량 통계를 반환합니다.")
def read_usage_stats():
    usage_stats = get_usage_stats()
    return usage_stats

@admin_router.get("/logs", summary="최근 요약 로그 조회", description="최근 100건의 요약 API 호출 로그를 반환합니다.")
def read_recent_logs():
    recent_logs = get_recent_logs()
    return recent_logs
