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

    # 각 스타일에 대한 용도 설명 추가
    general_description = "Provides a neutral, balanced summary of the content."
    problem_solver_description = "Focuses on summarizing the solution and the problem-solving process."
    emotion_focused_description = "Highlights the emotional aspects and feelings expressed in the content."

class TextInput(BaseModel):
    content: constr(min_length=10)
    option: SummaryOption
    style: SummaryStyle = Field(
        default=SummaryStyle.general,
        description=(
            "Choose a summary style: \n"
            "general: Provides a neutral, balanced summary (default).\n"
            "problem_solver: Focuses on the solution and problem-solving process.\n"
            "emotion_focused: Highlights the emotional aspects and feelings."
        )
    )

    class Config:
        json_schema_extra = {
            "example": {
                "content": "FastAPI를 사용하여 긴 텍스트를 간단히 요약하는 예시입니다.",
                "option": "medium",
                "style": "general"
            }
        }
