from pydantic import BaseModel, constr, Field
from enum import Enum

class SummaryOption(str, Enum):
    short = "short"
    medium = "medium"
    long = "long"

class SummaryStyle(str, Enum):
    general = "general"
    problem_solver = "problem_solver"
    emotion_focused = "emotion_focused"

class TextInput(BaseModel):
    content: constr(min_length=10)
    option: SummaryOption
    style: SummaryStyle = Field(
        default=SummaryStyle.general,
        description="Choose a summary style: general (default), problem_solver, or emotion_focused."
    )

    class Config:
        schema_extra = {
            "example": {
                "content": "FastAPI를 사용하여 긴 텍스트를 간단히 요약하는 예시입니다.",
                "option": "medium",
                "style": "general"
            }
        }
