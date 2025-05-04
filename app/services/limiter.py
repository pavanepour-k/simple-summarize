import asyncio
from app.config.redis_client import RedisClient
from app.config.settings import settings
from app.utils.error_handler import raise_http_exception
from datetime import datetime

async def increment_request_count(api_key: str, hour: int):
    try:
        redis_client = await RedisClient.instance()  # Redis 클라이언트 가져오기
        # 시간대별 요청 수 증가 (시간별로 요청 수를 관리)
        await redis_client.retry_command('HINCRBY', f"{api_key}:hourly:{hour}", "count", 1)
        await redis_client.retry_command('EXPIRE', f"{api_key}:hourly:{hour}", 86400)  # 24시간 유효
        return await redis_client.execute('HGET', f"{api_key}:hourly:{hour}", "count")  # 현재 요청 수 조회
    except Exception as e:
        raise_http_exception(f"Failed to increment request count: {str(e)}", code=500)

async def log_api_call(api_key: str, hour: int):
    """API 호출 로그를 Redis에 기록합니다."""
    try:
        redis_client = await RedisClient.instance()
        # 호출 로그 저장
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        await redis_client.retry_command('LPUSH', f"{api_key}:call_logs", timestamp)
        await redis_client.retry_command('LTRIM', f"{api_key}:call_logs", 0, 99)  # 최근 100개 로그만 저장
    except Exception as e:
        raise_http_exception(f"Failed to log API call: {str(e)}", code=500)

async def check_rate_limit(api_key: str, role: str, plan: str):
    """API 호출 제한을 체크하고 초과 시 에러를 발생시킵니다."""
    try:
        current_hour = datetime.now().hour  # 현재 시간 가져오기
        limit = get_plan_limit(role, plan)  # 동적으로 호출 제한 값 반환
        time_based_limit = get_time_based_limit(role, plan, current_hour)  # 시간대별 호출 제한

        # 전체 호출 제한을 시간대별 제한과 합산하여 적용
        limit = min(limit, time_based_limit)

        current_count = await increment_request_count(api_key, current_hour)
        await log_api_call(api_key, current_hour)  # API 호출 로그 기록

        if current_count > limit:
            raise_http_exception(f"Rate limit exceeded. Current: {current_count}, Limit: {limit}", code=429)
    except Exception as e:
        raise_http_exception(f"Rate limit check failed: {str(e)}", code=500)

# 각 요금제 및 역할별 호출 제한 설정
def get_plan_limit(role: str, plan: str):
    """PLAN_RATE_LIMIT에서 동적으로 호출 제한 값을 반환합니다."""
    role = role.lower()
    plan = plan.lower()
    return PLAN_RATE_LIMIT.get(role, PLAN_RATE_LIMIT["user"]).get(plan, PLAN_RATE_LIMIT["user"]["free"])
