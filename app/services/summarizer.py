from app.services.model_loader import model_loader  # ModelLoader 싱글톤 인스턴스 불러오기
import logging
from fastapi import HTTPException

# 로거 초기화
logger = logging.getLogger(__name__)

class SummarizerService:
    """언어별 모델을 사용하여 텍스트 요약을 처리하는 서비스."""
    
    def __init__(self, model_loader=model_loader):
        """
        SummarizerService 초기화 (ModelLoader 인스턴스)
        
        :param model_loader: 모델 로딩을 관리할 ModelLoader 인스턴스 (기본값: 싱글톤)
        """
        self.model_loader = model_loader

    def summarize(self, text: str, lang: str, style_prompt: str = ""):
        """
        주어진 텍스트를 지정된 언어 모델로 요약합니다.
        
        :param text: 요약할 입력 텍스트
        :param lang: 언어 코드 ('en', 'ko', 'ja' 등)
        :param style_prompt: 스타일 맞춤을 위한 선택적 프롬프트 (기본값은 없음)
        
        :return: 요약된 텍스트
        """
        try:
            # 언어에 맞는 모델 파이프라인 로드
            model_pipeline = self.model_loader.get_pipeline(lang)
            
            # 스타일 프롬프트가 있으면 입력 텍스트에 추가
            input_text = f"{style_prompt} {text}" if style_prompt else text
            
            # 요약 실행
            result = model_pipeline(input_text)
            
            # 요약 텍스트 반환
            return result[0]['summary_text']
        
        except KeyError as e:
            # 언어 모델이 없으면 'en' 모델로 fallback
            logger.error(f"{lang} 모델을 찾을 수 없어 'en' 모델로 변경. 에러: {e}")
            model_pipeline = self.model_loader.get_pipeline('en')
            result = model_pipeline(input_text)
            return result[0]['summary_text']
        
        except Exception as e:
            # 예외 발생 시 에러 로그 출력 후 HTTPException 반환
            logger.error(f"요약 중 오류 발생: {e}")
            raise HTTPException(status_code=500, detail=f"{lang} 언어로 텍스트 요약 중 오류가 발생했습니다. 모델 설정이나 입력을 확인해주세요.")
