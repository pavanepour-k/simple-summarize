# Rate Limit Configuration Guide

This document outlines how to configure and use plan-based rate limiting in the service.

---

## 🔧 Environment Variables

| Variable           | Description                                         | Example                |
| ------------------ | --------------------------------------------------- | ---------------------- |
| `PLAN_CONFIG`      | Plan key to apply to current execution context      | `user`, `pro`, `admin` |
| `PLAN_CONFIG_FILE` | Path to external JSON plan configuration (optional) | `./config/plan.json`   |

---

## 🧩 Plan JSON Schema

Each plan is a key-value object with the following structure:

```json
{
  "user": {
    "label": "Free User",
    "is_pro": false,
    "limits": {
      "daytime": {
        "rate_limit_per_minute": 10,
        "max_requests_per_day": 100,
        "max_concurrent_jobs": 2
      },
      "night": {
        "rate_limit_per_minute": 5,
        "max_requests_per_day": 50,
        "max_concurrent_jobs": 1
      }
    }
  },
  "pro": {
    "label": "Pro User",
    "is_pro": true,
    "limits": {
      "daytime": {
        "rate_limit_per_minute": 100,
        "max_requests_per_day": 1000,
        "max_concurrent_jobs": 10
      },
      "night": {
        "rate_limit_per_minute": 50,
        "max_requests_per_day": 500,
        "max_concurrent_jobs": 5
      }
    }
  }
}
```

---

## 📌 Notes

* `limits` must contain at least one slot (`daytime`, `night`, or `anytime`).
* If the given `slot` is not found, the system attempts to use the `anytime` fallback.
* All numeric values must be positive integers.
* If `PLAN_CONFIG_FILE` is malformed or missing, the app exits with `sys.exit(1)`.

---

## 🔄 Reloading Plans

You can reload updated configurations during runtime via:

```python
await reload_plans()
```

On success, it logs:

```
INFO Plan config reloaded, N plans
```

> NOTE: Reload is concurrency-safe via `asyncio.Lock()`.

---

## 🛡 Type Safety

* Each plan and its limits are validated using `Pydantic`.
* Structures are deeply immutable using `MappingProxyType` and `frozen=True` models.

---

## ✅ Recommended Defaults

If no valid plan is found via `PLAN_CONFIG`, `user` is used by default.
