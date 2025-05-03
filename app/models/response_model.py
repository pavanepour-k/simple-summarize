from pydantic import BaseModel, Field
from typing import Optional

class SummaryOutput(BaseModel):
    summary: str = Field(..., description="the summarized text")
    length: str = Field(..., description="summarization length option")
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
