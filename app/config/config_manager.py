import json
import logging
import os
from app.config.settings import settings
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

logger = logging.getLogger(__name__)

class Config:
    """환경별 설정을 관리하는 클래스"""
    
    def __init__(self):
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.model_config = None
        self._load_configurations()

    def _load_configurations(self):
        """환경에 맞는 설정 파일 로드"""
        if self.environment == "production":
            self._load_production_config()
        else:
            self._load_development_config()

    def _load_production_config(self):
        """생산 환경 설정 로드"""
        try:
            config_path = os.getenv("MODEL_CONFIG_PATH", 'app/config/models_production.json')
            with open(config_path, 'r', encoding='utf-8') as f:
                self.model_config = json.load(f)
            logger.info("Production 환경 설정을 성공적으로 로드했습니다.")
        except Exception as e:
            logger.error(f"Production 설정 파일 로딩 실패: {str(e)}")
            raise Exception("생산 환경 설정 로딩에 실패했습니다.")
    
    def _load_development_config(self):
        """개발 환경 설정 로드"""
        try:
            config_path = os.getenv("MODEL_CONFIG_PATH", 'app/config/models_development.json')
            with open(config_path, 'r', encoding='utf-8') as f:
                self.model_config = json.load(f)
            logger.info("Development 환경 설정을 성공적으로 로드했습니다.")
        except Exception as e:
            logger.error(f"Development 설정 파일 로딩 실패: {str(e)}")
            raise Exception("개발 환경 설정 로딩에 실패했습니다.")

    def get_model_config(self):
        """설정된 모델 경로 반환"""
        return self.model_config


# Config 인스턴스를 사용하여 환경 설정을 불러옵니다.
config = Config()

