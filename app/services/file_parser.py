from fastapi import UploadFile
from app.utils.error_handler import raise_http_exception
import fitz
import docx
from io import BytesIO

async def extract_text_from_file(file: UploadFile) -> str:
    try:
        contents = await file.read()
        if file.filename.endswith(".pdf"):
            return extract_from_pdf(contents)
        elif file.filename.endswith(".docx"):
            return extract_from_docx(contents)
        else:
            raise ValueError("Unsupported file type (.pdf, .docx only)")
    except Exception as e:
        raise_http_exception(f"File processing error: {str(e)}")

def extract_from_pdf(file_bytes: bytes) -> str:
    try:
        with fitz.open(stream=file_bytes, filetype="pdf") as doc:
            return "".join(page.get_text() for page in doc)
    except Exception as e:
        raise_http_exception(f"PDF extraction failed: {str(e)}")

def extract_from_docx(file_bytes: bytes) -> str:
    try:
        doc = docx.Document(BytesIO(file_bytes))
        return "\n".join(para.text for para in doc.paragraphs)
    except Exception as e:
        raise_http_exception(f"DOCX extraction failed: {str(e)}")
