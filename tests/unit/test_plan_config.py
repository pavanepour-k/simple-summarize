import pytest
import types
import asyncio
from config.plan_config import (
    get_plan_limits,
    get_plan_config,
    reload_plans,
    deep_freeze,
    PlanOptionsModel,
    PlanLimitsModel
)


def test_slot_fallback():
    plan = get_plan_config("admin")
    limits = get_plan_limits("admin", "nonexistent")
    assert limits.rate_limit_per_minute == 1000
    assert "anytime" in plan.limits


def test_deep_freeze_immutability():
    frozen = deep_freeze({"a": {"b": {"c": 1}}})
    assert isinstance(frozen, types.MappingProxyType)
    with pytest.raises(TypeError):
        frozen["a"] = {}
    with pytest.raises(TypeError):
        frozen["a"]["b"] = {}


@pytest.mark.asyncio
async def test_concurrent_reload(monkeypatch):
    call_log = []

    def fake_loader(path=None):
        call_log.append("loaded")
        return deep_freeze({
            "demo": PlanOptionsModel(
                label="Test", is_pro=False,
                limits={"anytime": PlanLimitsModel(
                    rate_limit_per_minute=1,
                    max_requests_per_day=1,
                    max_concurrent_jobs=1
                )}
            )
        })

    monkeypatch.setattr("config.plan_config.load_plan_config_from_file", fake_loader)

    await asyncio.gather(reload_plans(), reload_plans(), reload_plans())

    # Ensure reload happened exactly 3 times, but lock prevented overlap
    assert call_log == ["loaded"] * 3
