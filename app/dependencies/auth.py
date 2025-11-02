"""
인증 관련 의존성

API 키 검증 등 인증과 관련된 의존성 함수들
"""

from typing import Optional

from fastapi import Depends, Header
from sqlalchemy.orm import Session

from app.exceptions import ErrorCodes, ApiError
from app.models.base import get_db
from app.repositories.api_key_repository import ApiKeyRepository


def get_api_key_repository(db: Session = Depends(get_db)) -> ApiKeyRepository:
    """API 키 Repository 의존성"""
    return ApiKeyRepository(db)


async def get_api_key_id(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    api_key_repo: ApiKeyRepository = Depends(get_api_key_repository),
) -> int:
    """
    헤더에서 API 키를 받아서 유효성 검증 후 api_key_id 반환

    이 함수는 모든 라우터(email, sms 등)에서 공통으로 사용할 수 있습니다.

    Args:
        x_api_key: X-API-Key 헤더 값
        api_key_repo: API 키 Repository

    Returns:
        int: 유효한 api_key_id
    """
    if not x_api_key:
        raise ApiError(
            message="X-API-Key 헤더가 필요합니다",
            error_code=ErrorCodes.API_KEY_MISSING,
            status_code=401,
        )

    # API 키로 데이터베이스에서 조회
    api_key_record = await api_key_repo.get_by_api_key(x_api_key)

    if not api_key_record:
        raise ApiError(
            message="유효하지 않은 API 키입니다",
            error_code=ErrorCodes.API_KEY_INVALID,
            status_code=401,
        )

    if not api_key_record.is_active:
        raise ApiError(
            message="비활성화된 API 키입니다",
            error_code=ErrorCodes.API_KEY_INACTIVE,
            status_code=401,
        )

    return api_key_record.id
