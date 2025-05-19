from fastapi import APIRouter, Depends, Query
from app.security.auth import verify_admin
from app.services.analytics import get_usage_stats, get_recent_logs
from typing import Dict

# Admin router with dependency injection
admin_router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    dependencies=[Depends(verify_admin)],  # Admin authentication required
)


@admin_router.get(
    "/stats",
    summary="System usage statistics",
    description="Returns API usage statistics",
    response_model=Dict[str, int],
)
async def read_usage_stats():
    # Get system-wide usage stats
    return await get_usage_stats()


@admin_router.get(
    "/logs",
    summary="Recent summary logs",
    description="Returns the most recent API call logs",
)
async def read_recent_logs(
    limit: int = Query(100, description="Max logs to return", ge=1, le=1000)
):
    # Get recent API logs
    logs = await get_recent_logs()
    return logs[:limit]  # Apply limit
