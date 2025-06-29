from __future__ import annotations

from io import BytesIO
from pathlib import Path

from fastapi import UploadFile

from app.core.config import get_settings
from app.core.exceptions import BadRequestException, FileTooLargeException


class FileHandlerService:
    async def validate_file(self, file: UploadFile) -> None:
        settings = get_settings()
        if not file.filename:
            raise BadRequestException("Filename required")
        
        ext = Path(file.filename).suffix.lower()
        if ext not in settings.ALLOWED_EXTENSIONS:
            raise BadRequestException(f"Invalid file type: {ext}")
        
        content = await file.read()
        await file.seek(0)
        
        if len(content) > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
            raise FileTooLargeException(settings.MAX_FILE_SIZE_MB)
    
    async def extract_text(self, file: UploadFile) -> str:
        await self.validate_file(file)
        content = await file.read()
        ext = Path(file.filename).suffix.lower()
        
        if ext == ".pdf":
            return self._extract_pdf(content)
        elif ext == ".docx":
            return self._extract_docx(content)
        else:
            return content.decode("utf-8", errors="replace")
    
    def _extract_pdf(self, content: bytes) -> str:
        import fitz
        with fitz.open(stream=content, filetype="pdf") as doc:
            return "".join(page.get_text() for page in doc)
    
    def _extract_docx(self, content: bytes) -> str:
        import docx
        doc = docx.Document(BytesIO(content))
        return "\n".join(p.text for p in doc.paragraphs if p.text)