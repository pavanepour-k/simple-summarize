import logging
from fastapi import HTTPException
from app.services.model_loader import model_loader  # ModelLoader singleton instance
from enum import Enum

# Initialize logger
logger = logging.getLogger(__name__)

# Check model related libraries
try:
    import torch
    import tensorflow
    import flax
except ImportError as e:
    logger.error(
        f"Model libraries missing: {e.name}. Please ensure all dependencies are installed."
    )
    raise HTTPException(
        status_code=500,
        detail="Required model libraries are missing. Please check installation.",
    )


# Define summary styles Enum
class SummaryStyle(Enum):
    GENERAL = "general"
    PROBLEM_SOLVING = "problem_solving"
    EMOTIONAL = "emotional"


# Define summary length Enum
class SummaryOption(Enum):
    SHORT = "short"
    MEDIUM = "medium"
    LONG = "long"


# Style prompt mapping
STYLE_PROMPT_MAPPING = {
    SummaryStyle.GENERAL: "Summarize this text in a neutral and concise manner.",
    SummaryStyle.PROBLEM_SOLVING: "Summarize this text, focusing on the solution and problem-solving aspects.",
    SummaryStyle.EMOTIONAL: "Summarize this text with an emotional tone, capturing the feelings and emotions expressed.",
}

# Summary length settings
SUMMARY_LENGTH_MAPPING = {
    SummaryOption.SHORT: {"max_length": 50, "min_length": 25},
    SummaryOption.MEDIUM: {"max_length": 150, "min_length": 80},
    SummaryOption.LONG: {"max_length": 300, "min_length": 150},
}


class SummarizerService:
    # Service to process text summarization using language models

    def __init__(self, model_loader=model_loader):
        # Initialize SummarizerService (ModelLoader instance)
        self.model_loader = model_loader

    def summarize(
        self,
        text: str,
        lang: str,
        style: SummaryStyle = SummaryStyle.GENERAL,
        option: SummaryOption = SummaryOption.MEDIUM,
    ):
        # Summarize the given text using the selected language model
        try:
            # Choose the style prompt
            style_prompt = STYLE_PROMPT_MAPPING.get(
                style, STYLE_PROMPT_MAPPING[SummaryStyle.GENERAL]
            )

            # Set max_length and min_length according to summary length
            length_params = SUMMARY_LENGTH_MAPPING.get(
                option, SUMMARY_LENGTH_MAPPING[SummaryOption.MEDIUM]
            )

            # Load the model pipeline for the specified language
            model_pipeline = self.model_loader.get_pipeline(lang)

            # Add the style prompt to the input text
            input_text = f"{style_prompt} {text}"

            # Perform summarization
            result = model_pipeline(
                input_text,
                max_length=length_params["max_length"],
                min_length=length_params["min_length"],
            )

            # Return summarized text
            return result[0]["summary_text"]

        except KeyError as e:
            # Fallback to 'en' model if the language model is not found
            logger.error(
                f"Could not find {lang} model, falling back to 'en'. Error: {e}"
            )
            model_pipeline = self.model_loader.get_pipeline("en")
            result = model_pipeline(
                input_text,
                max_length=length_params["max_length"],
                min_length=length_params["min_length"],
            )
            return result[0]["summary_text"]

        except Exception as e:
            # Log the error and raise an HTTP exception
            logger.error(f"Error during summarization: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Error summarizing text in {lang}. Please check model settings or input.",
            )
