from __future__ import annotations

import asyncio
from collections import defaultdict
from datetime import datetime
from typing import Dict, List

import redis.asyncio as redis

from app.core.config import get_settings


class StatisticsService:
    def __init__(self):
        self._stats = defaultdict(int)
        self._logs = []
        self._redis = None
    
    async def _get_redis(self):
        if not self._redis:
            settings = get_settings()
            self._redis = await redis.from_url(settings.REDIS_URL)
        return self._redis
    
    async def record_usage(self, api_key: str, language: str, style: str):
        timestamp = datetime.utcnow()
        key_prefix = timestamp.strftime("%Y-%m-%d")
        
        self._stats[f"{key_prefix}:total"] += 1
        self._stats[f"{key_prefix}:lang:{language}"] += 1
        self._stats[f"{key_prefix}:style:{style}"] += 1
        
        log_entry = {
            "time": timestamp.isoformat(),
            "api_key": api_key,
            "language": language,
            "style": style
        }
        
        self._logs.append(log_entry)
        self._logs = self._logs[-1000:]
        
        try:
            r = await self._get_redis()
            await r.lpush("summary_logs", str(log_entry))
        except:
            pass
    
    def get_stats(self) -> Dict[str, int]:
        return dict(self._stats)
    
    def get_logs(self, limit: int = 100) -> List[Dict]:
        return self._logs[-limit:]