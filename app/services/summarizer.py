import logging
from fastapi import HTTPException
from app.services.model_loader import model_loader  # ModelLoader 싱글톤 인스턴스 불러오기
from enum import Enum

# 로거 초기화
logger = logging.getLogger(__name__)

# 모델 관련 라이브러리 체크
try:
    import torch
    import tensorflow
    import flax
except ImportError as e:
    logger.error(f"모델 관련 라이브러리 누락: {e.name}. 모든 의존성이 설치되었는지 확인해주세요.")
    raise HTTPException(status_code=500, detail="필수 모델 라이브러리가 누락되었습니다. 설치를 확인해주세요.")

# 요약 스타일을 정의하는 Enum
class SummaryStyle(Enum):
    GENERAL = "general"
    PROBLEM_SOLVING = "problem_solving"
    EMOTIONAL = "emotional"

# 스타일별 프롬프트 매핑
STYLE_PROMPT_MAPPING = {
    SummaryStyle.GENERAL: "Summarize this text in a neutral and concise manner.",
    SummaryStyle.PROBLEM_SOLVING: "Summarize this text, focusing on the solution and problem-solving aspects.",
    SummaryStyle.EMOTIONAL: "Summarize this text with an emotional tone, capturing the feelings and emotions expressed."
}

class SummarizerService:
# 언어별 모델을 사용하여 텍스트 요약을 처리하는 서비스
    
    def __init__(self, model_loader=model_loader):
        """
        SummarizerService 초기화 (ModelLoader 인스턴스)
        
        :param model_loader: 모델 로딩을 관리할 ModelLoader 인스턴스 (기본값: 싱글톤)
        """
        self.model_loader = model_loader

    def summarize(self, text: str, lang: str, style: SummaryStyle = SummaryStyle.GENERAL):
        """
        주어진 텍스트를 지정된 언어 모델로 요약합니다.
        
        :param text: 요약할 입력 텍스트
        :param lang: 언어 코드 ('en', 'ko', 'ja' 등)
        :param style: 스타일 맞춤을 위한 선택적 요약 스타일 (기본값: 일반)
        
        :return: 요약된 텍스트
        """
        try:
            # 스타일에 맞는 프롬프트 선택
            style_prompt = STYLE_PROMPT_MAPPING.get(style, STYLE_PROMPT_MAPPING[SummaryStyle.GENERAL])
            
            # 언어에 맞는 모델 파이프라인 로드
            model_pipeline = self.model_loader.get_pipeline(lang)
            
            # 스타일 프롬프트가 있으면 입력 텍스트에 추가
            input_text = f"{style_prompt} {text}"
            
            # 요약 실행
            result = model_pipeline(input_text)
            
            # 요약 텍스트 반환
            return result[0]['summary_text']
        
        except KeyError as e:
            # 언어 모델이 없으면 'en' 모델로 fallback
            logger.error(f"{lang} 모델을 찾을 수 없어 'en' 모델로 변경. 에러: {e}")
            raise HTTPException(status_code=415, detail=f"E101: Model '{lang}' not found, defaulting to 'en'.")
        
        except Exception as e:
            # 예외 발생 시 에러 로그 출력 후 HTTPException 반환
            logger.error(f"요약 중 오류 발생: {e}")
            raise HTTPException(status_code=500, detail=f"E102: Failed to summarize text in {lang}. Please check model or input.")
