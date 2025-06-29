from __future__ import annotations

from pydantic import BaseModel


class FileUploadResponse(BaseModel):
    filename: str
    size: int
    content_type: str
    text_length: int