from pydantic import BaseModel, Field
from typing import Optional
import os


class SummaryOutput(BaseModel):
    summary: str = Field(..., description="The summarized text")
    length: str = Field(
        ..., description="Summarization length option"
    )  # e.g. short/medium/long
    input_length: Optional[int] = Field(None, description="Original input text length")
    language: Optional[str] = Field(
        None, description="Detected language code (e.g., en, ko, ja)"
    )
    style: Optional[str] = Field(
        None,
        description="Applied summary style (general, problem_solver, or emotion_focused)",
    )
    role: Optional[str] = Field(
        default=None, description="API caller role: admin or user"
    )
    style_prompt: Optional[str] = Field(
        None,
        description=(
            "The style prompt used for summarization "
            "(used for debugging and traceability)"
        ),
    )  # For debugging

    @classmethod
    def create(cls, **kwargs):
        if not os.getenv("DEBUG_MODE", "false").lower() == "true":
            kwargs.pop("style_prompt", None)  # Remove style_prompt if not in debug mode
        return super().create(**kwargs)
