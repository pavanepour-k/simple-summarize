import asyncio
import redis.asyncio as redis
from app.utils.error_handler import raise_http_exception
from app.config.settings import settings

class RedisClient:
    _instance = None
    _client = None
    _lock = asyncio.Lock()

    def __init__(self):
        self._redis_pool = None

    @classmethod
    async def instance(cls):
        """Redis 클라이언트의 싱글턴 인스턴스를 반환합니다."""
        if cls._instance is None:
            async with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
                    await cls._instance._initialize_redis()
        return cls._instance

    async def _initialize_redis(self):
        """Redis 클라이언트 초기화 (메모리 정책 포함)"""
        try:
            self._redis_pool = redis.from_url(
                f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}",
                encoding='utf-8',
                minsize=5,  # 최소 연결 수
                maxsize=20,  # 최대 연결 수 (성능 테스트 후 최적화)
                timeout=10,  # 연결 타임아웃 설정
                retry_on_timeout=True,  # 타임아웃 시 재시도
                health_check_interval=60,  # 연결 상태 점검 간격 (초)
                max_connections=100,  # 최대 연결 수 (설정)
            )
            # 메모리 관리 정책 설정 (e.g., volatile-lru, allkeys-lru)
            await self.execute('CONFIG SET', 'maxmemory-policy', 'allkeys-lru')
        except Exception as e:
            raise_http_exception(f"Failed to connect to Redis: {str(e)}")

    async def get_client(self):
        """Redis 클라이언트를 반환합니다."""
        if not self._redis_pool:
            await self._initialize_redis()
        return self._redis_pool

    async def close(self):
        """Redis 클라이언트 연결을 닫습니다."""
        if self._redis_pool:
            await self._redis_pool.close()

    async def execute(self, command, *args):
        """Redis 커맨드를 비동기적으로 실행합니다."""
        client = await self.get_client()
        return await client.execute(command, *args)

    async def retry_command(self, command, *args, retries=3, delay=1):
        """Redis 커맨드 재시도 로직 (백프레셔 처리)"""
        attempt = 0
        while attempt < retries:
            try:
                return await self.execute(command, *args)
            except redis.RedisError as e:
                attempt += 1
                if attempt >= retries:
                    raise_http_exception(f"Redis command failed after {retries} retries: {str(e)}")
                await asyncio.sleep(delay ** attempt)  # 지수 백오프

