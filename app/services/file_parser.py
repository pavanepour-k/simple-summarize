import os
import logging
from io import BytesIO
from fastapi import UploadFile
from app.utils.error_handler import raise_http_exception
from app.config.settings import settings

# 로깅 설정
logger = logging.getLogger(__name__)

# 최대 파일 크기 설정
MAX_FILE_SIZE_MB = settings.MAX_FILE_SIZE_MB
MAX_FILE_SIZE = MAX_FILE_SIZE_MB * 1024 * 1024  # MB를 바이트로 변환

# 허용되는 파일 확장자
ALLOWED_EXTENSIONS = [".pdf", ".docx", ".txt", ".md"]

# 모델 관련 라이브러리 체크
try:
    import torch
    import tensorflow
    import flax
except ImportError as e:
    logger.error(f"모델 관련 라이브러리 누락: {e.name}")
    raise_http_exception("필수 모델 라이브러리가 누락되었습니다", code=500)

def validate_file_type(filename: str):
# 파일 형식 검증
    if not filename:
        raise_http_exception("Filename is required", code=400)
        
    file_extension = os.path.splitext(filename)[1].lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        supported_formats = ", ".join(ALLOWED_EXTENSIONS)
        raise_http_exception(
            f"Unsupported file type: {file_extension}. Allowed formats are: {supported_formats}.", 
            code=415
        )

def validate_file_size(file_size: int):
# 파일 크기 검증
    if file_size > MAX_FILE_SIZE:
        raise_http_exception(
            f"File size exceeds {MAX_FILE_SIZE_MB} MB", 
            code=413
        )

async def validate_file(file: UploadFile):
# 파일 검증 함수
    validate_file_type(file.filename)
    
    # FastAPI UploadFile은 파일 크기 속성이 없음
    content = await file.read()
    file_size = len(content)
    await file.seek(0)
    
    validate_file_size(file_size)
    return file_size

async def extract_text_from_file(file: UploadFile) -> str:
# 파일에서 텍스트 추출
    try:
        # 파일 검증
        await validate_file(file)
        
        # 파일 내용 읽기
        contents = await file.read()
        
        # 파일 형식에 맞춰 텍스트 추출
        if file.filename.lower().endswith(".pdf"):
            return extract_from_pdf(contents)
        elif file.filename.lower().endswith(".docx"):
            return extract_from_docx(contents)
        elif file.filename.lower().endswith((".txt", ".md")):
            # 텍스트 파일 디코딩
            return contents.decode("utf-8", errors="replace")
        else:
            raise_http_exception("Unsupported file format", code=415)
            
    except ValueError as e:
        # 파일 처리 오류
        logger.error(f"File processing error: {str(e)}")
        raise_http_exception(f"File processing error: {str(e)}", code=400)
    except Exception as e:
        # 예기치 않은 오류
        logger.error(f"Unexpected error processing file: {str(e)}", exc_info=True)
        raise_http_exception(f"Failed to process file: {str(e)}", code=500)
    finally:
        # 파일 포인터 초기화
        try:
            await file.seek(0)
        except Exception:
            pass

def extract_from_pdf(file_bytes: bytes) -> str:
# PDF 파일에서 텍스트 추출
    try:
        import fitz
        
        with fitz.open(stream=file_bytes, filetype="pdf") as doc:
            if doc.page_count == 0:
                raise ValueError("The PDF file is empty or invalid")
            
            # 모든 페이지에서 텍스트 추출
            text = ""
            for page in doc:
                text += page.get_text()
            
            return text
    except ImportError:
        logger.error("PyMuPDF (fitz) library not available")
        raise_http_exception("PDF processing is not available", code=501)
    except Exception as e:
        logger.error(f"PDF extraction error: {str(e)}", exc_info=True)
        raise_http_exception(f"Failed to extract text from PDF: {str(e)}", code=500)

def extract_from_docx(file_bytes: bytes) -> str:
# DOCX 파일에서 텍스트 추출
    try:
        import docx
        
        doc = docx.Document(BytesIO(file_bytes))
        
        if not doc.paragraphs:
            raise ValueError("The DOCX file is empty or invalid")
            
        # 모든 단락에서 텍스트 추출
        text = "\n".join(para.text for para in doc.paragraphs if para.text)
        
        return text
    except ImportError:
        logger.error("python-docx library not available")
        raise_http_exception("DOCX processing is not available", code=501)
    except Exception as e:
        logger.error(f"DOCX extraction error: {str(e)}", exc_info=True)
        raise_http_exception(f"Failed to extract text from DOCX: {str(e)}", code=500)
