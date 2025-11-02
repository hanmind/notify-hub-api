"""
예외 핸들러 모듈

FastAPI 애플리케이션에서 발생하는 예외들을 처리하는 핸들러들을 정의합니다.
"""

import traceback

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

from .base import ApiError
from .error_codes import ErrorCodes


async def api_exception_handler(request: Request, exc: ApiError) -> JSONResponse:
    """
    ApiError 커스텀 예외 핸들러
    
    Args:
        request: FastAPI Request 객체
        exc: 발생한 ApiError 예외 객체
        
    Returns:
        JSONResponse: 에러 정보를 포함한 JSON 응답
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "message": exc.message,
                "error_code": exc.error_code,
                "status_code": exc.status_code,
            }
        },
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    예상치 못한 HTTPException 처리를 위한 기본 핸들러

    커스텀 에러로 처리하지 못한 HTTPException들을 일관된 형태로 응답

    Args:
        request: FastAPI 요청 객체
        exc: 발생한 HTTPException 예외 객체

    Returns:
        JSONResponse: 일관된 형태의 JSON 에러 응답
    """
    # 에러 트레이스백 저장 (디버깅용)
    request.state.error_traceback = traceback.format_exc()

    # 상태 코드별 기본 에러 코드 매핑
    error_code_mapping = {
        400: ErrorCodes.VALIDATION_ERROR,
        401: ErrorCodes.API_KEY_INVALID,
        403: ErrorCodes.INSUFFICIENT_PERMISSION,
        404: ErrorCodes.RECORD_NOT_FOUND,
        422: ErrorCodes.REQUEST_PARSING_ERROR,
        500: ErrorCodes.INTERNAL_SERVER_ERROR,
    }

    error_code = error_code_mapping.get(exc.status_code, ErrorCodes.UNKNOWN_ERROR)

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "message": exc.detail if exc.detail else "알 수 없는 오류가 발생했습니다",
                "error_code": error_code,
                "status_code": exc.status_code,
            }
        },
    )
