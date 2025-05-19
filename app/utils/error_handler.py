from fastapi import HTTPException, status
import logging

logger = logging.getLogger("uvicorn.error")


# Function to raise an HTTP exception with appropriate status code
def raise_http_exception(
    detail: str, code=status.HTTP_400_BAD_REQUEST, log_message: str = None
):
    # Log error message based on the type of exception
    if log_message:
        logger.warning(log_message)
    else:
        logger.warning(f"Error raised: {detail}")

    # Raise HTTPException with the provided details
    raise HTTPException(status_code=code, detail={"error": detail})


# Detailed exception handling functions


# Handle bad request error (400)
def raise_bad_request(detail: str):
    raise_http_exception(
        detail, code=status.HTTP_400_BAD_REQUEST, log_message=f"Bad Request: {detail}"
    )


# Handle unauthorized error (401)
def raise_unauthorized(detail: str):
    raise_http_exception(
        detail,
        code=status.HTTP_401_UNAUTHORIZED,
        log_message=f"Unauthorized Access: {detail}",
    )


# Handle forbidden error (403)
def raise_forbidden(detail: str):
    raise_http_exception(
        detail,
        code=status.HTTP_403_FORBIDDEN,
        log_message=f"Forbidden Access: {detail}",
    )


# Handle not found error (404)
def raise_not_found(detail: str):
    raise_http_exception(
        detail, code=status.HTTP_404_NOT_FOUND, log_message=f"Not Found: {detail}"
    )


# Handle internal server error (500)
def raise_internal_server_error(detail: str):
    raise_http_exception(
        detail,
        code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        log_message=f"Internal Server Error: {detail}",
    )
