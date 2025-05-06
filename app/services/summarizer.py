import asyncio
from app.models.response_model import SummaryOutput
from app.models.request_model import SummaryStyle, SummaryOption
from app.config.plan_config import PlanConfigService
import os
from typing import Dict, Any

class SummarizerService:
    def __init__(self, lang: str = None, plan_config_service: PlanConfigService = None):
        self.lang = lang
        self.plan_config_service = plan_config_service or PlanConfigService()
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

        style_prompt = self._generate_style_prompt(style)
        if style_prompt:
            routed_content = style_prompt + routed_content

        # Get appropriate model for the language
        model_path = self.plan_config_service.get_model_for_language(self.lang)
        
        # Run model inference asynchronously
        max_len = self.length_mapping.get(option, 250)
        summarized_text = await self._run_model_async(model_path, routed_content, max_len)
        
        # Create response object
        response = SummaryOutput(
            summary=summarized_text,
            length=option.value,
            input_length=len(content),
            language=self.lang,
            style=style.value,
        )

        # Add style_prompt for debugging if enabled
        if os.getenv("DEBUG_MODE", "false").lower() == "true":
            response.style_prompt = style_prompt
        
        return response
        
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