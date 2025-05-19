import redis
import asyncio
from contextlib import asynccontextmanager
from app.utils.error_handler import raise_http_exception
from app.config.settings import settings


class RedisClient:
    _instance = None
    _lock = asyncio.Lock()
    _pool = None

    @classmethod
    async def instance(cls):
        # Return a singleton instance of RedisClient with async support
        if cls._instance is None:
            async with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
                    await cls._instance._initialize_redis()
        return cls._instance

    async def _initialize_redis(self):
        # Initialize Redis connection pool with optimal settings
        try:
            self._pool = redis.ConnectionPool(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                decode_responses=True,
                max_connections=settings.REDIS_MAX_CONNECTIONS,
                socket_timeout=10,
                retry_on_timeout=True,
            )
        except Exception as e:
            raise_http_exception(
                f"Failed to initialize Redis connection pool: {str(e)}", code=500
            )

    def get_connection(self):
        # Get a Redis connection from the pool
        if not self._pool:
            raise_http_exception("Redis connection pool not initialized", code=500)
        return redis.Redis(connection_pool=self._pool)

    @asynccontextmanager
    async def get_client(self):
        # Context manager for Redis connections
        conn = None
        try:
            conn = self.get_connection()
            yield conn
        finally:
            if conn:
                # Return connection to pool, not actually closing it
                pass

    async def execute(self, command, *args):
        # Execute a Redis command with proper error handling
        async with self.get_client() as client:
            try:
                return client.execute_command(command, *args)
            except redis.RedisError as e:
                raise_http_exception(f"Redis command failed: {str(e)}", code=500)

    async def retry_command(self, command, *args, retries=3, delay=1):
        # Execute a Redis command with retry logic and exponential backoff
        attempt = 0
        while attempt < retries:
            try:
                async with self.get_client() as client:
                    return client.execute_command(command, *args)
            except redis.RedisError as e:
                attempt += 1
                if attempt >= retries:
                    raise_http_exception(
                        f"Redis command failed after {retries} retries: {str(e)}",
                        code=500,
                    )
                await asyncio.sleep(delay * (2 ** (attempt - 1)))  # Exponential backoff
