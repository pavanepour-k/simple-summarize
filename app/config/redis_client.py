import redis
<<<<<<< HEAD
=======
import asyncio
import time
from contextlib import asynccontextmanager
>>>>>>> dev
from app.utils.error_handler import raise_http_exception
from app.config.settings import settings

class RedisClient:
    _instance = None
<<<<<<< HEAD
    _client = None
    _lock = None

    def __init__(self):
        self._redis_client = None

    @classmethod
    def instance(cls):
        """Redis 클라이언트의 싱글턴 인스턴스를 반환합니다."""
        if cls._instance is None:
            cls._instance = cls()
            cls._instance._initialize_redis()
        return cls._instance

    def _initialize_redis(self):
        """Redis 클라이언트 초기화 (메모리 정책 포함)"""
        try:
            self._redis_client = redis.StrictRedis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                encoding='utf-8',
                minsize=5,  # 최소 연결 수
                maxsize=20,  # 최대 연결 수 (성능 테스트 후 최적화)
                socket_timeout=10,  # 연결 타임아웃 설정
                retry_on_timeout=True,  # 타임아웃 시 재시도
            )
            # 메모리 관리 정책 설정 (e.g., volatile-lru, allkeys-lru)
            self._redis_client.config_set('maxmemory-policy', 'allkeys-lru')
        except Exception as e:
            raise_http_exception(f"Failed to connect to Redis: {str(e)}")

    def get_client(self):
        """Redis 클라이언트를 반환합니다."""
        if not self._redis_client:
            self._initialize_redis()
        return self._redis_client

    def close(self):
        """Redis 클라이언트 연결을 닫습니다."""
        if self._redis_client:
            self._redis_client.connection_pool.disconnect()

    def execute(self, command, *args):
        """Redis 커맨드를 동기적으로 실행합니다."""
        client = self.get_client()
        return client.execute_command(command, *args)

    def retry_command(self, command, *args, retries=3, delay=1):
        """Redis 커맨드 재시도 로직 (백프레셔 처리)"""
        attempt = 0
        while attempt < retries:
            try:
                return self.execute(command, *args)
            except redis.RedisError as e:
                attempt += 1
                if attempt >= retries:
                    raise_http_exception(f"Redis command failed after {retries} retries: {str(e)}")
                time.sleep(delay ** attempt)  # 지수 백오프
=======
    _lock = asyncio.Lock()
    _pool = None

    @classmethod
    async def instance(cls):
        """Return a singleton instance of RedisClient with async support"""
        if cls._instance is None:
            async with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
                    await cls._instance._initialize_redis()
        return cls._instance

    async def _initialize_redis(self):
        """Initialize Redis connection pool with optimal settings"""
        try:
            self._pool = redis.ConnectionPool(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                decode_responses=True,
                max_connections=settings.REDIS_MAX_CONNECTIONS,
                socket_timeout=10,
                retry_on_timeout=True
            )
        except Exception as e:
            raise_http_exception(f"Failed to initialize Redis connection pool: {str(e)}", code=500)

    def get_connection(self):
        """Get a Redis connection from the pool"""
        if not self._pool:
            raise_http_exception("Redis connection pool not initialized", code=500)
        return redis.Redis(connection_pool=self._pool)

    @asynccontextmanager
    async def get_client(self):
        """Context manager for Redis connections"""
        conn = None
        try:
            conn = self.get_connection()
            yield conn
        finally:
            if conn:
                # Return connection to pool, not actually closing it
                pass

    async def execute(self, command, *args):
        """Execute a Redis command with proper error handling"""
        async with self.get_client() as client:
            try:
                return client.execute_command(command, *args)
            except redis.RedisError as e:
                raise_http_exception(f"Redis command failed: {str(e)}", code=500)

    async def retry_command(self, command, *args, retries=3, delay=1):
        """Execute a Redis command with retry logic and exponential backoff"""
        attempt = 0
        while attempt < retries:
            try:
                async with self.get_client() as client:
                    return client.execute_command(command, *args)
            except redis.RedisError as e:
                attempt += 1
                if attempt >= retries:
                    raise_http_exception(f"Redis command failed after {retries} retries: {str(e)}", code=500)
                await asyncio.sleep(delay * (2 ** (attempt - 1)))  # Exponential backoff
>>>>>>> dev
