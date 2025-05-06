from fastapi import UploadFile
from app.utils.error_handler import raise_http_exception
import fitz
import docx
from io import BytesIO
import os
from app.config.settings import settings

# 최대 파일 크기 설정 (MB 단위로 .env 파일에서 설정)
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", 10))  # 기본값 10MB
MAX_FILE_SIZE = MAX_FILE_SIZE_MB * 1024 * 1024  # 바이트 단위로 변환

# 허용되는 파일 형식
ALLOWED_EXTENSIONS = [".pdf", ".docx"]

# 파일 크기 검사 함수
def validate_file_size(file: UploadFile):
    if file.size > MAX_FILE_SIZE:
        raise_http_exception("File size exceeds the maximum limit.", code=413)

# 파일 형식 검사 함수
def validate_file_type(file: UploadFile):
    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        raise_http_exception("Unsupported file type. Only .pdf and .docx are allowed.", code=415)

# 파일 유효성 검사 함수
async def validate_file(file: UploadFile):
    validate_file_size(file)  # 파일 크기 검사
    validate_file_extension(file)  # 파일 형식 검사

# 파일에서 텍스트 추출하는 함수
async def extract_text_from_file(file: UploadFile) -> str:
    try:
        await validate_file(file)  # 파일 크기 및 형식 검사

        contents = await file.read()
        # PDF 파일 처리
        if file.filename.endswith(".pdf"):
            return extract_from_pdf(contents)
        # DOCX 파일 처리
        elif file.filename.endswith(".docx"):
            return extract_from_docx(contents)
        else:
            raise ValueError("Unsupported file type. Only .pdf and .docx are allowed.")
    except ValueError as e:
        # 파일 형식에 대한 예외 처리
        raise_http_exception("File processing error.")
    except Exception as e:
        # 기타 모든 예외 처리
        raise_http_exception(f"An unexpected error occurred while processing the file: {str(e)}")

# PDF 파일에서 텍스트 추출하는 함수
def extract_from_pdf(file_bytes: bytes) -> str:
    try:
        # PDF 형식이 아닌 파일이 전달될 경우 예외 처리
        with fitz.open(stream=file_bytes, filetype="pdf") as doc:
            if doc.page_count == 0:
                raise ValueError("The PDF file is empty.")
            return "".join(page.get_text() for page in doc)
    except ValueError as e:
        raise_http_exception(f"PDF file error: {str(e)}")
    except Exception as e:
        raise_http_exception(f"Failed to extract text from PDF file: {str(e)}")

# DOCX 파일에서 텍스트 추출하는 함수
def extract_from_docx(file_bytes: bytes) -> str:
    try:
        doc = docx.Document(BytesIO(file_bytes))
        if not doc.paragraphs:
            raise ValueError("The DOCX file is empty.")
        return "\n".join(para.text for para in doc.paragraphs)
    except ValueError as e:
        raise_http_exception(f"DOCX file error: {str(e)}")
    except Exception as e:
        raise_http_exception(f"Failed to extract text from DOCX file: {str(e)}")
