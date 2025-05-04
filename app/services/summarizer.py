from app.models.response_model import SummaryOutput
from app.config.plan_config import get_model_for_language  # 모델 경로는 plan_config에서 가져옵니다
import os

# 서비스 계층으로 비즈니스 로직 분리
class SummarizerService:
    def __init__(self, lang: str = None):
        self.lang = lang

    def _route_content(self, content: str) -> str:
        # 언어에 맞는 내용 라우팅
        return language_routing(content, self.lang)

    def _generate_style_prompt(self, style: SummaryStyle) -> str:
        # 스타일에 맞는 프롬프트 생성
        style_prompt = ""
        if style == SummaryStyle.problem_solver:
            style_prompt = "Please summarize this content by focusing on identifying problems and their solutions:\n"
        elif style == SummaryStyle.emotion_focused:
            style_prompt = "Summarize the emotional or opinionated aspects of the following content:\n"
        return style_prompt

    def summarize(self, content: str, option: SummaryOption, style: SummaryStyle = SummaryStyle.general) -> SummaryOutput:
        if not self.lang:
            self.lang = detect_language(content)  # 언어를 감지합니다.

        routed_content = self._route_content(content)

        style_prompt = self._generate_style_prompt(style)
        if style_prompt:
            routed_content = style_prompt + routed_content

        # 모델을 호출하여 텍스트 요약
        model = get_model_for_language(self.lang)
        max_len = length_mapping[option]
        result = model(routed_content, max_length=max_len, min_length=20, do_sample=False)
        
        summary_text = result[0].get("summary_text") or result[0].get("generated_text", "")

        response = SummaryOutput(
            summary=summary_text,
            length=option.value,
            input_length=len(content),
            language=self.lang,
            style=style.value,
        )

        if os.getenv("DEBUG_MODE", "false").lower() == "true":
            response.style_prompt = style_prompt  # 디버깅 모드일 경우에만 style_prompt 필드를 포함
        
        return response

# summarize_text 함수는 SummarizerService로 대체됩니다.
def summarize_text(content: str, option: SummaryOption, style: SummaryStyle = SummaryStyle.general, lang: str = None) -> SummaryOutput:
    summarizer_service = SummarizerService(lang)
    return summarizer_service.summarize(content, option, style)
