from fastapi import APIRouter, Depends, Query

from app.api.auth import require_admin
from app.services.statistics import StatisticsService

router = APIRouter(prefix="/admin", tags=["Admin"], dependencies=[Depends(require_admin)])


@router.get("/stats")
async def get_stats(stats: StatisticsService = Depends()):
    return stats.get_stats()


@router.get("/logs")
async def get_logs(
    limit: int = Query(100, ge=1, le=1000),
    stats: StatisticsService = Depends()
):
    return stats.get_logs(limit)