from fastapi import UploadFile, HTTPException
import fitz  # PyMuPDF
import docx

async def extract_text_from_file(file: UploadFile) -> str:
    try:
        contents = await file.read()
        if file.filename.endswith(".pdf"):
            return extract_from_pdf(contents)
        elif file.filename.endswith(".docx"):
            return extract_from_docx(contents)
        else:
            raise ValueError("Unsupported file type. Supported types: .pdf, .docx")
    except ValueError as e:
        raise HTTPException(status_code=400, detail={"error": f"File type error: {str(e)}"})
    except Exception as e:
        raise HTTPException(status_code=400, detail={"error": f"Error while processing the file: {str(e)}"})

def extract_from_pdf(file_bytes: bytes) -> str:
    text = ""
    try:
        with fitz.open(stream=file_bytes, filetype="pdf") as doc:
            for page in doc:
                text += page.get_text()
    except Exception as e:
        raise HTTPException(status_code=400, detail={"error": f"Error while extracting PDF text: {str(e)}"})
    return text

def extract_from_docx(file_bytes: bytes) -> str:
    from io import BytesIO
    text = ""
    try:
        doc = docx.Document(BytesIO(file_bytes))
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        raise HTTPException(status_code=400, detail={"error": f"Error while extracting DOCX text: {str(e)}"})
    return text
