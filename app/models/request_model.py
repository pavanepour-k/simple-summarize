from pydantic import BaseModel, constr
from enum import Enum

class SummaryOption(str, Enum):
    short = "short"
    medium = "medium"
    long = "long"

class TextInput(BaseModel):
    content: constr(min_length=10)
    option: SummaryOption

    class Config:
        schema_extra = {
            "example": {
                "content": "FastAPI를 사용하여 긴 텍스트를 요약하는 예시입니다. 이 예시는 최소 10자 이상이어야 합니다.",
                "option": "medium"
            }
        }
