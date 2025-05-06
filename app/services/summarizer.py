<<<<<<< HEAD
from app.models.response_model import SummaryOutput
from app.models.request_model import SummaryStyle, SummaryOption
from app.config.plan_config import PlanConfigService  # 모델 경로를 가져오는 서비스
import os
=======
import asyncio
from app.models.response_model import SummaryOutput
from app.models.request_model import SummaryStyle, SummaryOption
from app.config.plan_config import PlanConfigService
import os
from typing import Dict, Any
>>>>>>> dev

class SummarizerService:
    def __init__(self, lang: str = None, plan_config_service: PlanConfigService = None):
        self.lang = lang
        self.plan_config_service = plan_config_service or PlanConfigService()
<<<<<<< HEAD

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

=======
        self.length_mapping = {
            SummaryOption.short: 100,
            SummaryOption.medium: 250,
            SummaryOption.long: 500
        }

    async def detect_language_async(self, content: str) -> str:
        """Detect language asynchronously to avoid blocking"""
        # This would use a library like langdetect, but wrap it in async
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._detect_language, content)

    def _detect_language(self, content: str) -> str:
        """Synchronous language detection (to be executed in a thread pool)"""
        # Language detection logic
        # For example: return langdetect.detect(content)
        return "en"  # Default to English for this example
        
    async def _route_content(self, content: str) -> str:
        """Route content based on language asynchronously"""
        if not self.lang:
            self.lang = await self.detect_language_async(content)
        return content  # Simplified for example

    def _generate_style_prompt(self, style: SummaryStyle) -> str:
        """Generate style-specific prompts"""
        style_prompts = {
            SummaryStyle.problem_solver: "Please summarize this content by focusing on identifying problems and their solutions:\n",
            SummaryStyle.emotion_focused: "Summarize the emotional or opinionated aspects of the following content:\n",
            SummaryStyle.general: ""
        }
        return style_prompts.get(style, "")

    async def summarize_async(self, content: str, option: SummaryOption, style: SummaryStyle = SummaryStyle.general) -> SummaryOutput:
        """Asynchronous summarization method"""
        if not self.lang:
            self.lang = await self.detect_language_async(content)  # Detect language asynchronously

        routed_content = await self._route_content(content)

>>>>>>> dev
        style_prompt = self._generate_style_prompt(style)
        if style_prompt:
            routed_content = style_prompt + routed_content

<<<<<<< HEAD
        # 모델을 호출하여 텍스트 요약
        model = get_model_for_language(self.lang)
        max_len = length_mapping[option]
        result = model(routed_content, max_length=max_len, min_length=20, do_sample=False)
        
        summarize_text = result[0].get("summarize_text") or result[0].get("generated_text", "")

        response = SummaryOutput(
            summary=summarize_text,
=======
        # Get appropriate model for the language
        model_path = self.plan_config_service.get_model_for_language(self.lang)
        
        # Run model inference asynchronously
        max_len = self.length_mapping.get(option, 250)
        summarized_text = await self._run_model_async(model_path, routed_content, max_len)
        
        # Create response object
        response = SummaryOutput(
            summary=summarized_text,
>>>>>>> dev
            length=option.value,
            input_length=len(content),
            language=self.lang,
            style=style.value,
        )

<<<<<<< HEAD
        # 디버깅 모드일 경우에만 style_prompt 필드를 포함
=======
        # Add style_prompt for debugging if enabled
>>>>>>> dev
        if os.getenv("DEBUG_MODE", "false").lower() == "true":
            response.style_prompt = style_prompt
        
        return response
<<<<<<< HEAD


class PlanConfigService:
    def __init__(self):
        self.model_paths = self._load_model_paths()

    def _load_model_paths(self) -> dict:
        """모델 경로를 설정 파일에서 로드하는 함수"""
        try:
            with open("config/models.json", 'r') as file:
                return json.load(file)
        except Exception as e:
            raise Exception(f"Failed to load model paths from config file: {str(e)}")

    def get_model_for_language(self, lang: str) -> str:
        """언어에 해당하는 모델 경로를 반환"""
        return self.model_paths.get(lang, self.model_paths["en"])  # 기본값으로 영어 모델을 반환

    def get_time_based_limit(self, role: str, plan: str, hour: int) -> int:
        """시간대에 따른 API 호출 제한"""
        time_limits = {
            "user": {
                0: 50, 6: 200, 12: 300, 18: 150,
            },
            "pro": {
                0: 100, 6: 500, 12: 1000, 18: 800,
            }
        }
        role = role.lower()
        plan = plan.lower()
        return time_limits.get(role, {}).get(hour, 100)  # 기본값 100개 제한
=======
        
    async def _run_model_async(self, model_path: str, content: str, max_len: int) -> str:
        """Run the model asynchronously"""
        # This would typically load and run the model
        # For this example, we'll just return a mock result
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._mock_model_inference, content, max_len)
    
    def _mock_model_inference(self, content: str, max_len: int) -> str:
        """Mock model inference (to be executed in a thread pool)"""
        # This would be replaced with actual model inference
        return f"Summary of: {content[:max_len//10]}..."
>>>>>>> dev
