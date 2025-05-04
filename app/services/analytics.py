import redis
import asyncio
from collections import defaultdict
from datetime import datetime
from typing import Dict, List
from pydantic import BaseModel
from app.config.settings import settings
import time

# 설정값 기반 로그 제한 및 배치 처리 최적화
MAX_LOG_ENTRIES = getattr(settings, "MAX_LOG_ENTRIES", 100)
BATCH_SIZE = getattr(settings, "LOG_BATCH_SIZE", 10)  # 배치 크기
BATCH_INTERVAL = getattr(settings, "LOG_BATCH_INTERVAL", 10)  # 배치 처리 주기 (초)
MAX_QUEUE_SIZE = getattr(settings, "MAX_QUEUE_SIZE", 1000)  # 큐 크기 제한

class LogEntry(BaseModel):
    time: str
    role: str
    language: str
    style: str

class SummaryAnalytics:
    _instance = None
    _lock = asyncio.Lock()  # 비동기 락 사용
    _log_queue = asyncio.Queue(maxsize=MAX_QUEUE_SIZE)  # 비동기 큐 크기 제한

    def __init__(self):
        self.stats_counter: Dict[str, int] = defaultdict(int)
        self.log_history: List[LogEntry] = []
        self.redis_client = None

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _initialize_redis(self):
        """Redis 클라이언트 초기화"""
        if not self.redis_client:
            self.redis_client = redis.StrictRedis(
                host='localhost',
                port=6379,
                db=0,
                decode_responses=True
            )

    async def _process_batch(self):
        """배치로 로그 처리"""
        while True:
            if self._log_queue.empty():
                await asyncio.sleep(BATCH_INTERVAL)  # 주기적으로 배치 처리 대기

            batch = []
            for _ in range(BATCH_SIZE):
                if not self._log_queue.empty():
                    batch.append(await self._log_queue.get())
                else:
                    break

            if batch:
                # Redis로 배치 로그 저장
                await self._save_logs_to_redis(batch)
                # 메모리 내 로그 기록 갱신
                for entry in batch:
                    self.log_history.append(entry)
                    if len(self.log_history) > MAX_LOG_ENTRIES:
                        self.log_history.pop(0)

    def _save_logs_to_redis(self, logs: List[LogEntry]):
        """Redis에 배치 로그 저장"""
        if not self.redis_client:
            self._initialize_redis()

        try:
            # Redis 파이프라인을 사용하여 배치로 처리
            pipe = self.redis_client.pipeline()
            for log in logs:
                log_data = log.dict()
                # Redis에 로그 저장 (채널 이름으로 logs 사용)
                pipe.lpush("logs", str(log_data))
            pipe.execute()
        except Exception as e:
            logger.error(f"Failed to save logs to Redis: {str(e)}")
            # Redis 장애 시 로컬 저장소로 로그 저장 (대체 처리)
            self._save_logs_locally(logs)

    def _save_logs_locally(self, logs: List[LogEntry]):
        """Redis 장애 시 로컬 파일에 임시 저장"""
        with open("local_logs.txt", "a") as f:
            for log in logs:
                f.write(f"{log.dict()}\n")
        logger.warning("Logs saved locally due to Redis failure.")

    async def record_usage(self, role: str, language: str, style: str):
        today = datetime.utcnow().strftime("%Y-%m-%d")
        self.stats_counter[f"{today}:total"] += 1
        self.stats_counter[f"{today}:role:{role}"] += 1
        self.stats_counter[f"{today}:lang:{language}"] += 1
        self.stats_counter[f"{today}:style:{style}"] += 1

        entry = LogEntry(
            time=datetime.utcnow().isoformat(),
            role=role,
            language=language,
            style=style
        )

        # 비동기 큐에 로그 추가
        await self._log_queue.put(entry)

    def get_stats(self) -> Dict[str, int]:
        return dict(self.stats_counter)

    def get_logs(self) -> List[Dict]:
        return [entry.dict() for entry in self.log_history]

    def reset(self):
        self.stats_counter.clear()
        self.log_history.clear()

# 비동기적으로 로그 기록 함수
async def record_summary_usage(role: str, language: str, style: str):
    await SummaryAnalytics.instance().record_usage(role, language, style)

def get_usage_stats() -> Dict[str, int]:
    return SummaryAnalytics.instance().get_stats()

def get_recent_logs() -> List[Dict]:
    return SummaryAnalytics.instance().get_logs()
