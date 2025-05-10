import os
import logging
from io import BytesIO
from fastapi import UploadFile
from app.utils.error_handler import raise_http_exception
from app.config.settings import settings

# Setup logging
logger = logging.getLogger(__name__)

# Get maximum file size from settings
MAX_FILE_SIZE_MB = settings.MAX_FILE_SIZE_MB
MAX_FILE_SIZE = MAX_FILE_SIZE_MB * 1024 * 1024  # Convert MB to bytes

# Allowed file extensions
ALLOWED_EXTENSIONS = [".pdf", ".docx", ".txt", ".md"]

# 모델 관련 라이브러리 체크
try:
    import torch
    import tensorflow
    import flax
except ImportError as e:
    logger.error(f"모델 관련 라이브러리 누락: {e.name}. 모든 의존성이 설치되었는지 확인해주세요.")
    raise_http_exception("필수 모델 라이브러리가 누락되었습니다. 설치를 확인해주세요.", code=500)

def validate_file_type(filename: str):

    if not filename:
        raise_http_exception("Filename is required", code=400)
        
    file_extension = os.path.splitext(filename)[1].lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        supported_formats = ", ".join(ALLOWED_EXTENSIONS)
        raise_http_exception(
            f"Unsupported file type. Allowed formats: {supported_formats}", 
            code=415
        )

def validate_file_size(file_size: int):

    if file_size > MAX_FILE_SIZE:
        raise_http_exception(
            f"File size exceeds the maximum limit of {MAX_FILE_SIZE_MB} MB", 
            code=413
        )

async def validate_file(file: UploadFile):

    validate_file_type(file.filename)
    
    # FastAPI's UploadFile doesn't have a size attribute
    # Need to read the file to determine its size
    content = await file.read()
    file_size = len(content)
    
    # Important: Seek back to the beginning after reading
    await file.seek(0)
    
    validate_file_size(file_size)
    return file_size

async def extract_text_from_file(file: UploadFile) -> str:
    try:
        # Validate file before processing
        await validate_file(file)
        
        # Read file content
        contents = await file.read()
        
        # Extract text based on file type
        if file.filename.lower().endswith(".pdf"):
            return extract_from_pdf(contents)
        elif file.filename.lower().endswith(".docx"):
            return extract_from_docx(contents)
        elif file.filename.lower().endswith((".txt", ".md")):
            # Decode plain text files
            return contents.decode("utf-8", errors="replace")
        else:
            raise_http_exception("Unsupported file type", code=415)
            
    except ValueError as e:
        # File format errors
        logger.error(f"File processing error: {str(e)}")
        raise_http_exception(f"File processing error: {str(e)}", code=400)
    except Exception as e:
        # Unexpected errors
        logger.error(f"Unexpected error processing file: {str(e)}", exc_info=True)
        raise_http_exception(f"Failed to process file: {str(e)}", code=500)
    finally:
        # Reset the file pointer position
        try:
            await file.seek(0)
        except Exception:
            pass

def extract_from_pdf(file_bytes: bytes) -> str:

    try:
        # Import here to avoid loading unless needed
        import fitz
        
        # Parse PDF file
        with fitz.open(stream=file_bytes, filetype="pdf") as doc:
            if doc.page_count == 0:
                raise ValueError("The PDF file is empty or invalid")
            
            # Extract text from all pages
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

    try:
        # Import here to avoid loading unless needed
        import docx
        
        # Parse DOCX file
        doc = docx.Document(BytesIO(file_bytes))
        
        if not doc.paragraphs:
            raise ValueError("The DOCX file is empty or invalid")
            
        # Extract text from all paragraphs
        text = "\n".join(para.text for para in doc.paragraphs if para.text)
        
        return text
    except ImportError:
        logger.error("python-docx library not available")
        raise_http_exception("DOCX processing is not available", code=501)
    except Exception as e:
        logger.error(f"DOCX extraction error: {str(e)}", exc_info=True)
        raise_http_exception(f"Failed to extract text from DOCX: {str(e)}", code=500)
