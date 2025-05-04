import redis
from app.utils.error_handler import raise_http_exception
from app.config.settings import settings

class RedisClient:
    _instance = None
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
