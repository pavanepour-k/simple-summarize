import redis
from app.utils.error_handler import raise_http_exception
from app.config.plan_config import get_plan_limit
from app.config.redis_client import redis_client

def increment_request_count(api_key: str):
    count = redis_client.incr(api_key)
    redis_client.expire(api_key, 86400)  # 24 hours
    return count

def check_rate_limit(api_key: str, role: str):
    limit = get_plan_limit(role)
    count = increment_request_count(api_key)
    if count > limit:
        raise_http_exception("Rate limit exceeded", code=429)