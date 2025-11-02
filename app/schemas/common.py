"""
공통 스키마 모델

여러 API에서 공통으로 사용되는 Pydantic 모델들
"""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class BaseResponse(BaseModel):
    """기본 응답 모델"""

    success: bool = True
    message: str = "요청이 성공적으로 처리되었습니다"
    timestamp: datetime = datetime.now()


class ErrorResponse(BaseModel):
    """에러 응답 모델"""

    success: bool = False
    error_code: str
    error_message: str
    timestamp: datetime = datetime.now()
    details: Optional[Dict[str, Any]] = None


class HealthResponse(BaseModel):
    """헬스체크 응답 모델"""

    status: str
    service: str
    version: str
    timestamp: str


class DetailedHealthResponse(HealthResponse):
    """상세 헬스체크 응답 모델"""

    components: Dict[str, str]
    uptime: str


# `~Params`: 쿼리 파라미터 스키마


class PaginationParams(BaseModel):
    """페이지네이션을 위한 쿼리 파라미터 스키마"""

    page: int = Field(
        default=0,
        ge=0,
        title="페이지 번호",
        description="조회할 페이지 번호 (0부터 시작)",
        example=0,
    )
    size: int = Field(
        default=10,
        ge=1,
        le=100,
        title="페이지 크기",
        description="한 페이지에 표시할 항목 수 (1-100)",
        example=10,
    )


class ScheduleFilterParams(BaseModel):
    """스케줄 목록 조회를 위한 필터링 파라미터 스키마"""

    status: Optional[str] = Field(
        default=None,
        title="스케줄 상태",
        description="필터링할 스케줄 상태 (예: PENDING, COMPLETED, CANCELLED)",
        example="PENDING",
    )
    limit: int = Field(
        default=100,
        ge=1,
        le=1000,
        title="조회 제한 수",
        description="한 번에 조회할 최대 항목 수 (1-1000)",
        example=100,
    )
    offset: int = Field(
        default=0,
        ge=0,
        title="건너뛸 항목 수",
        description="건너뛸 항목의 수",
        example=0,
    )
