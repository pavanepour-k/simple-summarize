from fastapi import HTTPException, status
import logging

logger = logging.getLogger("uvicorn.error")

def raise_http_exception(detail: str, code=status.HTTP_400_BAD_REQUEST):
    logger.warning(f"Error raised: {detail}")
    raise HTTPException(status_code=code, detail={"error": detail})
