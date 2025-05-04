from fastapi import HTTPException, status
import logging

logger = logging.getLogger("uvicorn.error")

# HTTPException을 세분화하여 처리
def raise_http_exception(detail: str, code=status.HTTP_400_BAD_REQUEST, log_message: str = None):
    """
    예외를 발생시키는 함수로, 상태 코드에 맞는 오류를 발생시킵니다.
    - detail: 오류의 상세 내용
    - code: HTTP 상태 코드 (기본값 400)
    - log_message: 로그로 남길 메시지 (선택적)
    """
    # 오류 유형에 맞는 로그 메시지 기록
    if log_message:
        logger.warning(log_message)
    else:
        logger.warning(f"Error raised: {detail}")
    
    # HTTPException 발생
    raise HTTPException(status_code=code, detail={"error": detail})

# 세부적인 예외 처리 함수들

# 사용자 입력 오류 (400 Bad Request)
def raise_bad_request(detail: str):
    raise_http_exception(detail, code=status.HTTP_400_BAD_REQUEST, log_message=f"Bad Request: {detail}")

# 인증 실패 (401 Unauthorized)
def raise_unauthorized(detail: str):
    raise_http_exception(detail, code=status.HTTP_401_UNAUTHORIZED, log_message=f"Unauthorized Access: {detail}")

# 권한 부족 (403 Forbidden)
def raise_forbidden(detail: str):
    raise_http_exception(detail, code=status.HTTP_403_FORBIDDEN, log_message=f"Forbidden Access: {detail}")

# 리소스 없음 (404 Not Found)
def raise_not_found(detail: str):
    raise_http_exception(detail, code=status.HTTP_404_NOT_FOUND, log_message=f"Not Found: {detail}")

# 내부 서버 오류 (500 Internal Server Error)
def raise_internal_server_error(detail: str):
    raise_http_exception(detail, code=status.HTTP_500_INTERNAL_SERVER_ERROR, log_message=f"Internal Server Error: {detail}")
