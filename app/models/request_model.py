from pydantic import BaseModel, constr, Field
from enum import Enum


class SummaryOption(str, Enum):
    short = "short"
    medium = "medium"
    long = "long"

    short_description = "Short summary with brief content (max 50 characters)."
    medium_description = "Medium summary with more detail (max 150 characters)."
    long_description = (
        "Long summary providing detailed information (max 300 characters)."
    )


class SummaryStyle(str, Enum):
    general = "general"
    problem_solver = "problem_solver"
    emotion_focused = "emotion_focused"

    general_description = "Provides a neutral, balanced summary of the content."
    problem_solver_description = (
        "Focuses on summarizing the solution and the problem-solving process."
    )
    emotion_focused_description = (
        "Highlights the emotional aspects and feelings expressed in the content."
    )


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
        ),
    )

    class Config:
        json_schema_extra = {
            "example": {
                "content": "Example of summarizing long text using FastAPI.",
                "option": "medium",
                "style": "general",
            }
        }
