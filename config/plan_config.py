import os
import json
import logging
import sys
import asyncio
from typing import Mapping, Any
from types import MappingProxyType
from pydantic import BaseModel, ValidationError, model_validator

logger = logging.getLogger(__name__)
_reload_lock = asyncio.Lock()

class PlanLimitsModel(BaseModel):
    rate_limit_per_minute: int
    max_requests_per_day: int
    max_concurrent_jobs: int

    model_config = {"frozen": True}


class PlanOptionsModel(BaseModel):
    label: str
    is_pro: bool
    limits: dict[str, PlanLimitsModel]

    model_config = {"frozen": True}

    @model_validator(mode="before")
    @classmethod
    def validate_limits(cls, values):
        limits = values.get("limits")
        if not isinstance(limits, dict):
            raise ValueError("'limits' must be a dict of time-slot keys")
        return values


PLAN_ENV_KEY = "PLAN_CONFIG"
DEFAULT_PLAN = "user"
PLANS: Mapping[str, PlanOptionsModel] = {}

PLANS_RAW: dict[str, dict] = {
    "admin": {
        "label": "Administrator",
        "is_pro": True,
        "limits": {
            "anytime": {
                "rate_limit_per_minute": 1000,
                "max_requests_per_day": 100000,
                "max_concurrent_jobs": 100,
            }
        },
    },
    "user": {
        "label": "Free User",
        "is_pro": False,
        "limits": {
            "daytime": {
                "rate_limit_per_minute": 10,
                "max_requests_per_day": 100,
                "max_concurrent_jobs": 2,
            },
            "night": {
                "rate_limit_per_minute": 5,
                "max_requests_per_day": 50,
                "max_concurrent_jobs": 1,
            },
        },
    },
    "pro": {
        "label": "Pro Subscriber",
        "is_pro": True,
        "limits": {
            "daytime": {
                "rate_limit_per_minute": 100,
                "max_requests_per_day": 1000,
                "max_concurrent_jobs": 10,
            },
            "night": {
                "rate_limit_per_minute": 50,
                "max_requests_per_day": 500,
                "max_concurrent_jobs": 5,
            },
        },
    },
}


def deep_freeze(obj: Any) -> Any:
    if isinstance(obj, dict):
        return MappingProxyType({k: deep_freeze(v) for k, v in obj.items()})
    return obj


def load_plan_config_from_file(path: str = None) -> Mapping[str, PlanOptionsModel]:
    data = None
    if path:
        try:
            with open(path, encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            logger.error("Failed to load PLAN_CONFIG_FILE '%s': %s", path, e)
            sys.exit(1)
    else:
        data = PLANS_RAW

    try:
        validated = {k: PlanOptionsModel(**v) for k, v in data.items()}
        return deep_freeze(validated)
    except ValidationError as ve:
        logger.error("Invalid plan config structure: %s", ve)
        sys.exit(1)


PLANS = load_plan_config_from_file(os.getenv("PLAN_CONFIG_FILE"))


async def reload_plans():
    global PLANS
    async with _reload_lock:
        PLANS = load_plan_config_from_file(os.getenv("PLAN_CONFIG_FILE"))
        logger.info("Plan config reloaded, %d plans", len(PLANS))


def get_plan_config(plan_key: str = None) -> PlanOptionsModel:
    key = (plan_key or os.getenv(PLAN_ENV_KEY, DEFAULT_PLAN)).strip().lower()
    return PLANS.get(key, PLANS[DEFAULT_PLAN])


def get_plan_limits(plan_key: str, slot: str) -> PlanLimitsModel:
    plan = get_plan_config(plan_key)
    slot_key = slot.strip().lower()
    return plan.limits.get(slot_key) or plan.limits.get("anytime") or _invalid_slot(plan_key, slot_key)


def _invalid_slot(plan_key: str, slot_key: str):
    raise ValueError(f"Invalid slot '{slot_key}' for plan '{plan_key}' and no 'anytime' fallback.")


def is_admin(user_roles: list[str]) -> bool:
    return "admin" in [role.strip().lower() for role in user_roles]
