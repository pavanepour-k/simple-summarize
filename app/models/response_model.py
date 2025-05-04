from pydantic import BaseModel, Field
from typing import Optional
import os

class SummaryOutput(BaseModel):
    summary: str = Field(..., description="the summarized text")
    length: str = Field(..., description="summarization length option")  # 예: short/medium/long
    input_length: Optional[int] = Field(
        None,
        description="original input text length"
    )
    language: Optional[str] = Field(
        None,
        description="Detected language code (e.g., en, ko, ja)"
    )
    style: Optional[str] = Field(
        None,
        description="applied summary style (general, problem_solver, or emotion_focused)"
    )
    role: Optional[str] = Field(
        default=None,
        description="API caller role: admin or user"
    )
    style_prompt: Optional[str] = Field(
        None,
        description="The style prompt used for summarization (used for debugging and traceability)"
    )  # 디버깅용 필드

    @classmethod
    def create(cls, **kwargs):
        if not os.getenv("DEBUG_MODE", "false").lower() == "true":
            kwargs.pop("style_prompt", None)  # 디버깅 모드가 아니면 style_prompt를 제외
        return super().create(**kwargs)
