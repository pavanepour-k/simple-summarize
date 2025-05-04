import asyncio
from app.config.redis_client import RedisClient
from app.config.settings import settings
from app.utils.error_handler import raise_http_exception

async def increment_request_count(api_key: str):
    try:
        redis_client = await RedisClient.instance()  # Redis 클라이언트 가져오기
        # 파이프라인을 사용하여 INCR과 EXPIRE를 한번에 처리
        await redis_client.retry_command('INCR', api_key)  # 요청 수 증가
        await redis_client.retry_command('EXPIRE', api_key, 86400)  # 24시간 유효
        return await redis_client.execute('GET', api_key)  # 현재 요청 수 조회
    except Exception as e:
        raise_http_exception(f"Failed to increment request count: {str(e)}", code=500)

async def check_rate_limit(api_key: str, role: str, plan: str):
    """API 호출 제한을 체크하고 초과시 에러를 발생시킵니다."""
    try:
        limit = get_plan_limit(role, plan)  # 동적으로 호출 제한 값 반환
        current_count = await increment_request_count(api_key)

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
