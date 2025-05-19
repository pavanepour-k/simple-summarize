import logging
from datetime import datetime
from app.config.redis_client import RedisClient
from app.utils.error_handler import raise_http_exception

# Initialize logger
logger = logging.getLogger(__name__)

# Plan rate limit (for demonstration purposes)
PLAN_RATE_LIMIT = {
    "user": {"free": 1000, "pro": 5000, "enterprise": 10000},
    "pro": {"free": 1000, "pro": 10000, "enterprise": 20000},
    "admin": {"free": 1000, "pro": 10000, "enterprise": 50000},
}


# Get the current limit for the plan and role
def get_plan_limit(role: str, plan: str):
    # Return the call limit dynamically from PLAN_RATE_LIMIT
    role = role.lower()
    plan = plan.lower()
    return PLAN_RATE_LIMIT.get(role, PLAN_RATE_LIMIT["user"]).get(
        plan, PLAN_RATE_LIMIT["user"]["free"]
    )


async def increment_request_count(api_key: str, hour: int):
    # Increment the request count for the given API key and hour
    try:
        redis_client = await RedisClient.instance()
        await redis_client.retry_command(
            "HINCRBY", f"{api_key}:hourly:{hour}", "count", 1
        )
        await redis_client.retry_command(
            "EXPIRE", f"{api_key}:hourly:{hour}", 86400
        )  # 24-hour validity
        return await redis_client.execute("HGET", f"{api_key}:hourly:{hour}", "count")
    except Exception as e:
        raise_http_exception(f"Failed to increment request count: {str(e)}", code=500)


async def log_api_call(api_key: str, hour: int):
    # Log the API call to Redis
    try:
        redis_client = await RedisClient.instance()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        await redis_client.retry_command("LPUSH", f"{api_key}:call_logs", timestamp)
        await redis_client.retry_command(
            "LTRIM", f"{api_key}:call_logs", 0, 99
        )  # Keep only the most recent 100 logs
    except Exception as e:
        raise_http_exception(f"Failed to log API call: {str(e)}", code=500)


async def check_rate_limit(api_key: str, role: str, plan: str):
    # Check the rate limit for API calls and raise an error if exceeded
    try:
        current_hour = datetime.now().hour  # Get current hour
        limit = get_plan_limit(role, plan)  # Get the call limit based on role and plan
        time_based_limit = get_time_based_limit(
            role, plan, current_hour
        )  # Get time-based rate limit

        # Apply the minimum of both limits
        limit = min(limit, time_based_limit)

        current_count = await increment_request_count(api_key, current_hour)
        await log_api_call(api_key, current_hour)  # Log the API call

        if current_count > limit:
            raise_http_exception(
                f"Rate limit exceeded. Current: {current_count}, Limit: {limit}",
                code=429,
            )
    except Exception as e:
        raise_http_exception(f"Rate limit check failed: {str(e)}", code=500)


async def get_time_based_limit(role: str, plan: str, hour: int) -> int:
    # Return the time-based API limit (e.g., based on the hour)
    time_limits = {
        "user": {0: 50, 6: 200, 12: 300, 18: 150},
        "pro": {0: 100, 6: 500, 12: 1000, 18: 800},
    }
    role = role.lower()
    time_limits_for_role = time_limits.get(role, time_limits["user"])

    return time_limits_for_role.get(hour, 100)  # Default limit is 100 calls
