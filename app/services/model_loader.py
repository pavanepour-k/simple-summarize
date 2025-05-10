import json
import logging
from transformers import pipeline
from functools import lru_cache
import os

# 로거 초기화
logger = logging.getLogger(__name__)

class ModelLoader:
    """언어별 모델을 관리하고 캐싱하는 싱글톤 클래스."""
    
    _instance = None
    _model_config = None
    
    def __new__(cls, *args, **kwargs):
        """ModelLoader의 인스턴스가 하나만 존재하도록 보장."""
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls._instance._load_model_config()  # 첫 번째 인스턴스가 생성될 때 모델 설정 로드
        return cls._instance

    def _load_model_config(self):
        """`models.json`에서 모델 설정을 로드."""
        try:
            # 환경변수에서 모델 설정 경로를 불러오고, 없으면 기본 경로 사용
            config_path = os.getenv("MODEL_CONFIG_PATH", 'app/config/models.json')  
            with open(config_path, 'r', encoding='utf-8') as f:
                self._model_config = json.load(f)
            logger.info("모델 설정을 성공적으로 로드했습니다.")
        except FileNotFoundError as e:
            logger.error(f"모델 설정 파일을 찾을 수 없습니다: {e}")
            raise Exception("모델 설정 파일을 찾을 수 없습니다.")
        except json.JSONDecodeError as e:
            logger.error(f"모델 설정 파일을 읽는 중 오류 발생: {e}")
            raise Exception("모델 설정 파일이 잘못된 JSON 형식입니다.")
        except Exception as e:
            logger.error(f"모델 설정 로딩 실패: {e}")
            raise Exception("모델 설정 로딩에 실패했습니다.")
    
    @lru_cache(maxsize=None)
    def get_pipeline(self, lang: str):
        """요청된 언어에 대한 요약 파이프라인을 반환."""
        # 지정된 언어에 맞는 모델명을 가져오고, 없으면 'en' 모델로 fallback
        model_name = self._model_config.get(lang, self._model_config.get('en'))
        
        try:
            # transformers 파이프라인을 사용하여 모델 로드
            return pipeline("summarization", model=model_name)
        except Exception as e:
            logger.error(f"모델 {model_name}을(를) 로드하는 중 오류 발생: {e}")
            # 모델 로딩 실패 시 'en' 모델로 fallback
            fallback_model_name = self._model_config.get('en')
            logger.info(f"기본 모델로 fallback: {fallback_model_name}")
            return pipeline("summarization", model=fallback_model_name)

# ModelLoader의 인스턴스 생성
model_loader = ModelLoader()
