import asyncio
from datetime import datetime
from typing import Dict, List
from pydantic import BaseModel
from app.config.redis_client import RedisClient
import logging

logger = logging.getLogger(__name__)


class LogEntry(BaseModel):
    time: str
    api_key: str
    language: str
    style: str


class SummaryAnalytics:
    _instance = None
    _lock = asyncio.Lock()
    _log_queue = None
    _batch_task = None

    def __init__(self):
        self.stats_counter = {}
        self.log_history = []
        self._log_queue = asyncio.Queue(maxsize=1000)

    @classmethod
    async def instance(cls):
        # Get or create the singleton instance
        if cls._instance is None:
            async with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
                    # Start background task for batch processing
                    cls._instance._batch_task = asyncio.create_task(
                        cls._instance._process_batch()
                    )
        return cls._instance

    async def _process_batch(self):
        # Process logs in batches to reduce Redis operations
        while True:
            try:
                # Wait for logs or process in batches
                if self._log_queue.empty():
                    await asyncio.sleep(10)  # Wait 10 seconds between batch processing
                    continue

                # Process up to 10 logs at once
                batch = []
                for _ in range(10):
                    if not self._log_queue.empty():
                        batch.append(await self._log_queue.get())
                    else:
                        break

                if batch:
                    # Save logs to Redis
                    await self._save_logs_to_redis(batch)

                    # Update in-memory log history
                    self.log_history.extend(batch)
                    if (
                        len(self.log_history) > 100
                    ):  # Keep only the most recent 100 logs
                        self.log_history = self.log_history[-100:]
            except Exception as e:
                logger.error(f"Error in batch processing: {str(e)}")
                await asyncio.sleep(5)  # Brief delay before retrying

    async def _save_logs_to_redis(self, logs: List[LogEntry]):
        # Save logs to Redis with proper connection handling
        redis_client = await RedisClient.instance()
        try:
            # Use pipeline for better performance
            async with redis_client.get_client() as client:
                pipe = client.pipeline()
                for log in logs:
                    log_data = log.model_dump_json()
                    pipe.lpush("summary_logs", log_data)
                pipe.execute()
        except Exception as e:
            logger.error(f"Failed to save logs to Redis: {str(e)}")
            # Fall back to local storage
            self._save_logs_locally(logs)

    def _save_logs_locally(self, logs: List[LogEntry]):
        # Save logs locally if Redis is unavailable
        try:
            with open("local_logs.txt", "a") as f:
                for log in logs:
                    f.write(f"{log.model_dump_json()}\n")
        except Exception as e:
            logger.error(f"Failed to save logs locally: {str(e)}")

    async def record_usage(self, api_key: str, language: str, style: str):
        # Record API usage with proper async handling
        today = datetime.utcnow().strftime("%Y-%m-%d")

        # Update in-memory counters
        key = f"{today}:total"
        self.stats_counter[key] = self.stats_counter.get(key, 0) + 1

        key = f"{today}:lang:{language}"
        self.stats_counter[key] = self.stats_counter.get(key, 0) + 1

        key = f"{today}:style:{style}"
        self.stats_counter[key] = self.stats_counter.get(key, 0) + 1

        # Create log entry
        entry = LogEntry(
            time=datetime.utcnow().isoformat(),
            api_key=api_key,
            language=language,
            style=style,
        )

        # Add to processing queue
        try:
            await self._log_queue.put(entry)
        except asyncio.QueueFull:
            logger.warning("Analytics queue full, dropping log entry")

    def get_stats(self) -> Dict[str, int]:
        # Get current usage statistics
        return dict(self.stats_counter)

    def get_logs(self) -> List[Dict]:
        # Get recent log entries
        return [entry.model_dump() for entry in self.log_history]


# Helper functions for external use
async def record_summary_usage(api_key: str, language: str, style: str):
    # Record summary usage asynchronously
    analytics = await SummaryAnalytics.instance()
    await analytics.record_usage(api_key, language, style)


async def get_usage_stats() -> Dict[str, int]:
    # Get usage statistics asynchronously
    analytics = await SummaryAnalytics.instance()
    return analytics.get_stats()


async def get_recent_logs() -> List[Dict]:
    # Get recent logs asynchronously
    analytics = await SummaryAnalytics.instance()
    return analytics.get_logs()
