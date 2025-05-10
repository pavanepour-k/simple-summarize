import logging
from app.config.config_manager import ConfigManager  # ConfigManager 불러오기

# 로거 초기화
logger = logging.getLogger(__name__)

class RateLimiter:
    """속도 제한을 처리하는 클래스"""
    
    def __init__(self):
        """
        RateLimiter 초기화
        ConfigManager는 기본적으로 싱글톤 사용
        """
        self.config_manager = ConfigManager.instance()

    def get_plan_limit(self, role: str, plan: str):
        """
        역할과 계획에 대한 제한을 가져옴
        
        :param role: 사용자 역할
        :param plan: 사용자 계획
        :return: 제한 값
        """
        try:
            # 계획 제한 가져오기
            limit = self.config_manager.get_plan_limit(role, plan)
            logger.info(f"'{role}' 역할의 '{plan}' 계획에 대한 제한: {limit}")
            return limit
        except KeyError as e:
            logger.error(f"제한 가져오기 오류: {role}, {plan}, 오류: {e}")
            raise ValueError("계획 제한을 가져오는 중 오류 발생")
        except Exception as e:
            logger.error(f"예상치 못한 오류: {e}")
            raise

    def get_time_based_limit(self, role: str, plan: str):
        """
        역할과 계획에 대한 시간 기반 제한을 가져옴
        
        :param role: 사용자 역할
        :param plan: 사용자 계획
        :return: 시간 기반 제한
        """
        try:
            # 시간 기반 제한 가져오기
            time_limit = self.config_manager.get_time_based_limit(role, plan)
            logger.info(f"'{role}' 역할의 '{plan}' 계획에 대한 시간 기반 제한: {time_limit}")
            return time_limit
        except KeyError as e:
            logger.error(f"시간 제한 가져오기 오류: {role}, {plan}, 오류: {e}")
            raise ValueError("시간 기반 제한을 가져오는 중 오류 발생")
        except Exception as e:
            logger.error(f"예상치 못한 오류: {e}")
            raise

    def is_within_limit(self, role: str, plan: str, request_count: int, time_elapsed: int):
        """
        요청 수와 경과 시간이 제한 내에 있는지 확인
        
        :param role: 사용자 역할
        :param plan: 사용자 계획
        :param request_count: 요청 수
        :param time_elapsed: 경과 시간
        :return: 제한 내 여부 (True/False)
        """
        plan_limit = self.get_plan_limit(role, plan)
        time_limit = self.get_time_based_limit(role, plan)
        
        if request_count <= plan_limit and time_elapsed <= time_limit:
            return True
        else:
            logger.warning(f"요청 수 {request_count} 또는 경과 시간 {time_elapsed} 초과")
            return False
