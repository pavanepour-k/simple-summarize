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
        description="detected language code"
    )
