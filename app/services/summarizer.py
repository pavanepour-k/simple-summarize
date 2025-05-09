import asyncio
import logging
import os
from typing import Dict, Any, Optional

try:
    import langdetect
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False

from app.models.response_model import SummaryOutput
from app.models.request_model import SummaryStyle, SummaryOption
from app.services.model_loader import get_model_loader
from app.utils.error_handler import raise_http_exception

logger = logging.getLogger(__name__)

class SummarizerService:

    
    def __init__(self, lang: str = None):

        self.lang = lang
        self.model_loader = get_model_loader()
        
        # Map summary options to target lengths
        self.length_mapping = {
            SummaryOption.short: 100,
            SummaryOption.medium: 250,
            SummaryOption.long: 500
        }
        
        # Map summary options to min_length values (30% of max length)
        self.min_length_mapping = {
            SummaryOption.short: 30,   # 30% of 100
            SummaryOption.medium: 75,  # 30% of 250
            SummaryOption.long: 150,   # 30% of 500
        }

    async def detect_language_async(self, content: str) -> str:
        if not LANGDETECT_AVAILABLE:
            logger.warning("Language detection library not available, defaulting to English")
            return "en"
            
        # Run detection in a thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        try:
            return await loop.run_in_executor(None, self._detect_language, content)
        except Exception as e:
            logger.error(f"Language detection error: {str(e)}")
            return "en"  # Default to English on failure

    def _detect_language(self, content: str) -> str:

        try:
            # Take a sample of the content for faster detection
            sample = content[:min(len(content), 1000)]
            return langdetect.detect(sample)
        except Exception as e:
            logger.error(f"Language detection failed: {str(e)}")
            return "en"  # Default to English
        
    async def _route_content(self, content: str) -> str:

        if not self.lang:
            self.lang = await self.detect_language_async(content)
        
        # Record the detected language in the logs
        logger.info(f"Content routed for language: {self.lang}")
        
        # Future enhancement: Implement language-specific preprocessing here
        return content

    def _generate_style_prompt(self, style: SummaryStyle) -> str:

        style_prompts = {
            SummaryStyle.problem_solver: "Please summarize this content by focusing on identifying problems and their solutions:\n",
            SummaryStyle.emotion_focused: "Summarize the emotional or opinionated aspects of the following content:\n",
            SummaryStyle.general: ""  # No special prompt for general style
        }
        return style_prompts.get(style, "")

    async def summarize_async(self, content: str, option: SummaryOption, style: SummaryStyle = SummaryStyle.general) -> SummaryOutput:

        try:
            # Detect language if not already set
            if not self.lang:
                self.lang = await self.detect_language_async(content)
                logger.info(f"Detected language: {self.lang}")

            # Process content based on language
            routed_content = await self._route_content(content)

            # Apply style-specific prompt if applicable
            style_prompt = self._generate_style_prompt(style)
            if style_prompt:
                routed_content = style_prompt + routed_content

            # Configure summary parameters
            max_len = self.length_mapping.get(option, 250)
            min_len = self.min_length_mapping.get(option, 75)
            
            # Run model inference asynchronously
            summarized_text = await self._run_model_async(
                self.lang, 
                routed_content, 
                max_len=max_len,
                min_len=min_len
            )
            
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
            
        except Exception as e:
            logger.error(f"Summarization error: {str(e)}", exc_info=True)
            raise_http_exception(f"Summarization failed: {str(e)}", code=500)
        
    async def _run_model_async(self, lang: str, content: str, max_len: int, min_len: int) -> str:

        try:
            # Run in thread pool to avoid blocking the event loop
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                None, 
                self._run_model_inference, 
                lang, 
                content, 
                max_len,
                min_len
            )
        except Exception as e:
            logger.error(f"Model inference error: {str(e)}", exc_info=True)
            raise_http_exception(f"Model inference failed: {str(e)}", code=500)
    
    def _run_model_inference(self, lang: str, content: str, max_len: int, min_len: int) -> str:

        try:
            # Get the appropriate pipeline for this language
            summarizer = self.model_loader.get_pipeline(lang)
            
            # Truncate input if it's extremely long to prevent OOM errors
            # Most models have context limits (e.g. 1024 tokens)
            max_input_length = 4096  # Adjust based on model constraints
            truncated_content = content[:max_input_length]
            
            # Generate summary
            summary_output = summarizer(
                truncated_content,
                max_length=max_len,
                min_length=min_len,
                do_sample=False  # Deterministic generation
            )
            
            # Extract the summary text
            if isinstance(summary_output, list) and len(summary_output) > 0:
                summary_text = summary_output[0].get('summary_text', '')
                return summary_text.strip()
            
            # Fallback for unexpected output format
            return "Summary could not be generated."
            
        except Exception as e:
            logger.error(f"Model inference error for language '{lang}': {str(e)}")
            
            # Fallback when in development/testing
            if os.getenv("DEBUG_MODE", "false").lower() == "true":
                return f"[DEBUG] Mock summary of: {content[:max_len//10]}..."
            
            # In production, propagate the error
            raise Exception(f"Summarization model inference failed: {str(e)}")