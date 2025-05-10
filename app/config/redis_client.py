import redis.asyncio as redis  # 비동기 Redis 클라이언트 사용
import asyncio
import logging

# 로거 초기화
logger = logging.getLogger(__name__)

class RedisClient:
    """비동기 Redis 작업 처리 클래스"""
    
    def __init__(self, host='localhost', port=6379, db=0):
        """
        RedisClient 초기화
        
        :param host: Redis 서버 호스트
        :param port: Redis 서버 포트
        :param db: Redis 데이터베이스 번호
        """
        self.redis = redis.Redis(host=host, port=port, db=db)

    async def execute_command(self, command, *args):
        """
        비동기 Redis 명령어 실행
        
        :param command: 실행할 Redis 명령어
        :param args: 명령어 인수들
        :return: 명령어 실행 결과
        """
        try:
            result = await self.redis.execute_command(command, *args)
            return result
        except Exception as e:
            logger.error(f"명령어 실행 오류: {command} 인수: {args}, 오류: {e}")
            raise

    async def set(self, key, value, ex=None):
        """Redis에 값 설정"""
        return await self.execute_command('SET', key, value, 'EX', ex) if ex else await self.execute_command('SET', key, value)

    async def get(self, key):
        """Redis에서 값 가져오기"""
        return await self.execute_command('GET', key)

    async def delete(self, key):
        """Redis에서 키 삭제"""
        return await self.execute_command('DEL', key)

    async def close(self):
        """Redis 연결 종료"""
        try:
            await self.redis.close()
            logger.info("Redis 연결 종료")
        except Exception as e:
            logger.error(f"연결 종료 오류: {e}")
