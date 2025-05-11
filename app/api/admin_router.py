from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List, Dict
from app.security.auth import verify_admin
from app.services.analytics import get_usage_stats, get_recent_logs

# Admin-only router with proper dependency injection
admin_router = APIRouter(
    prefix="/admin", 
    tags=["Admin"],  # API 문서에서 사용할 태그
    dependencies=[Depends(verify_admin)]  # 모든 라우트는 관리자 인증 필요
)

@admin_router.get(
    "/stats", 
    summary="System usage statistics",  # Swagger 문서에서 나타날 간략한 설명
    description="Returns API usage statistics",  # Swagger에서 API의 상세 설명
    response_model=Dict[str, int],  # 응답 모델 정의
    response_description="A dictionary of system-wide usage statistics"  # 응답에 대한 설명 추가
)
async def read_usage_stats():
    """
    Get system-wide usage statistics (admin only)
    
    - **Returns**: A dictionary containing system statistics (e.g., API usage counts)
    """
    try:
        stats = await get_usage_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving stats: {str(e)}")

@admin_router.get(
    "/logs", 
    summary="Recent summary logs",  # Swagger 문서에서 나타날 간략한 설명
    description="Returns the most recent API call logs",  # Swagger에서 API의 상세 설명
    response_model=List[Dict[str, str]],  # 응답 모델 정의 (로그는 리스트 형태)
    response_description="A list of recent API call logs"  # 응답에 대한 설명 추가
)
async def read_recent_logs(
    limit: int = Query(100, description="Maximum number of logs to return", ge=1, le=1000)
):
    """
    Get recent API usage logs (admin only)
    
    - **limit**: The maximum number of logs to return (between 1 and 1000)
    - **Returns**: A list of logs with metadata (e.g., timestamp, endpoint)
    """
    try:
        logs = await get_recent_logs()
        return logs[:limit]  # Apply limit parameter
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving logs: {str(e)}")
