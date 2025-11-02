"""
이메일 API 스키마

이메일 발송 관련 요청/응답 모델 정의
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, EmailStr, Field

# =============================================================================
# 베이스 클래스들
# =============================================================================


class BaseEmailContent(BaseModel):
    """이메일 콘텐츠 베이스 클래스"""

    subject: str = Field(
        ...,
        min_length=1,
        max_length=200,
        title="이메일 제목",
        description="이메일 제목 (1-200자)",
        example="환영합니다!",
    )
    html_body: str = Field(
        ...,
        min_length=1,
        title="이메일 HTML 내용",
        example="<h1>가입을 축하합니다!</h1><p>서비스에 오신 것을 환영합니다.</p>",
    )
    sender_address: Optional[EmailStr] = Field(
        None,
        title="발신자 이메일",
        description="발신자 이메일 주소 (미지정시 API 키 기반 자동 선택)",
        example="noreply@example.com",
    )


class BaseScheduleInfo(BaseModel):
    """스케줄 정보 베이스 클래스"""

    schedule_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        title="스케줄 이름",
        example="회원가입 환영 이메일",
    )
    scheduled_at: datetime = Field(
        ...,
        title="예약 실행 시간",
        description="예약 실행 시간 (UTC)",
        example="2024-06-20T10:00:00Z",
    )
    timezone: str = Field(default="UTC", title="시간대", example="Asia/Seoul")


class BaseRetrySettings(BaseModel):
    """재시도 설정 베이스 클래스"""

    max_retry: int = Field(default=3, ge=0, le=10, title="최대 재시도 횟수", example=3)
    retry_interval: int = Field(
        default=300,
        ge=60,
        le=3600,
        title="재시도 간격",
        description="재시도 간격 (초)",
        example=300,
    )


class BaseTemplateSettings(BaseModel):
    """템플릿 설정 베이스 클래스"""

    template_id: Optional[int] = Field(None, title="템플릿 ID", example=1)
    template_variables: Optional[Dict[str, Any]] = Field(
        None, title="템플릿 변수", example={"user_name": "홍길동"}
    )


class BaseApiResponse(BaseModel):
    """API 응답 베이스 클래스"""

    request_id: str = Field(
        ...,
        title="요청 ID",
        description="NCloud에서 반환한 고유 요청 ID",
        example="20250616000072163803",
    )
    timestamp: datetime = Field(
        default_factory=datetime.now,
        title="처리 시간",
        example="2025-06-16T13:52:40.634000",
    )


# =============================================================================
# 이메일 발송 스키마
# =============================================================================


class EmailRequest(BaseEmailContent):
    """단일 이메일 발송 요청"""

    to_email: EmailStr = Field(
        ..., title="수신자 이메일", example="user@example.com"
    )
    to_name: Optional[str] = Field(None, title="수신자 이름", example="홍길동")


class EmailRecipient(BaseModel):
    """이메일 수신자 정보"""

    email: EmailStr = Field(..., title="수신자 이메일 주소", example="user@example.com")
    name: Optional[str] = Field(None, title="수신자 이름", example="홍길동")


class BulkEmailRequest(BaseEmailContent):
    """대량 이메일 발송 요청"""

    recipients: List[EmailRecipient] = Field(
        ...,
        min_items=1,
        max_items=100,
        title="수신자 목록",
        description="이메일을 받을 수신자 목록 (최대 100명)",
        example=[
            {"email": "user1@example.com", "name": "홍길동"},
            {"email": "user2@example.com", "name": "김철수"},
        ],
    )


class EmailResponse(BaseApiResponse):
    """이메일 발송 응답"""

    success: bool = Field(default=True, title="발송 여부", example=True)
    message: str = Field(
        default="이메일이 성공적으로 발송되었습니다",
        title="응답 메시지",
        example="이메일이 성공적으로 발송되었습니다",
    )
    recipient_count: int = Field(..., title="수신자 수", example=1)


class EmailStatusResponse(BaseApiResponse):
    """이메일 상태 조회 응답"""

    status: str = Field(..., title="발송 상태", example="발송성공")
    details: Dict[str, Any] = Field(
        ...,
        title="상세 상태 정보",
        example={
            "mailId": "20250616000072135101",
            "emailStatus": {"label": "발송성공", "code": "S"},
        },
    )


class EmailListResponse(BaseApiResponse):
    """이메일 목록 조회 응답"""

    page: int = Field(..., title="현재 페이지", example=0)
    size: int = Field(..., title="페이지 크기", example=10)
    status: str = Field(..., title="조회 상태", example="조회 완료")
    details: Dict[str, Any] = Field(
        ...,
        title="페이징된 메일 목록 정보",
        example={
            "content": [
                {
                    "mailId": "20250616000072135101",
                    "title": "환영합니다!",
                    "emailStatus": {"label": "발송성공", "code": "S"},
                    "senderAddress": "noreply@example.com",
                    "representativeRecipient": "user@example.com",
                }
            ],
            "totalElements": 1,
            "totalPages": 1,
            "first": True,
            "last": True,
        },
    )


# =============================================================================
# 이메일 스케줄링 스키마
# =============================================================================


class EmailScheduleRequest(
    BaseScheduleInfo, BaseEmailContent, BaseTemplateSettings, BaseRetrySettings
):
    """이메일 스케줄 생성 요청"""

    # 수신자 정보
    to_email: EmailStr = Field(
        ..., title="수신자 이메일 주소", example="user@example.com"
    )
    to_name: Optional[str] = Field(None, title="수신자 이름", example="홍길동")


class BulkEmailScheduleRequest(
    BaseScheduleInfo, BaseEmailContent, BaseTemplateSettings, BaseRetrySettings
):
    """대량 이메일 스케줄 생성 요청"""

    # 대량 수신자 정보
    recipients: List[EmailRecipient] = Field(
        ...,
        min_items=1,
        max_items=100,
        title="수신자 목록",
        example=[
            {"email": "user1@example.com", "name": "홍길동"},
            {"email": "user2@example.com", "name": "김철수"},
        ],
    )


class EmailScheduleResponse(BaseModel):
    """이메일 스케줄 생성/조회 응답"""

    success: bool = Field(default=True, title="성공 여부", example=True)
    message: str = Field(
        ..., title="응답 메시지", example="이메일 스케줄이 생성되었습니다"
    )
    schedule_id: int = Field(..., title="생성된 스케줄 ID", example=123)
    schedule_name: str = Field(..., title="스케줄 이름", example="회원가입 환영 이메일")
    scheduled_at: datetime = Field(
        ..., title="예약 실행 시간", example="2024-06-20T10:00:00Z"
    )
    status: str = Field(..., title="스케줄 상태", example="pending")
    created_at: datetime = Field(..., title="생성 시간", example="2024-06-19T15:30:00Z")


class EmailScheduleListResponse(BaseModel):
    """이메일 스케줄 목록 조회 응답"""

    schedules: List[Dict[str, Any]] = Field(
        ...,
        title="스케줄 목록",
        example=[
            {
                "schedule_id": 123,
                "schedule_name": "회원가입 환영 이메일",
                "scheduled_at": "2024-06-20T10:00:00Z",
                "status": "pending",
            }
        ],
    )
    total_count: int = Field(..., title="전체 스케줄 수", example=1)
    page: int = Field(..., title="현재 페이지", example=0)
    size: int = Field(..., title="페이지 크기", example=10)


class EmailScheduleExecuteResponse(BaseModel):
    """이메일 스케줄 실행 응답"""

    message: str = Field(
        ..., title="실행 결과 메시지", example="스케줄이 성공적으로 실행되었습니다"
    )
    executed_count: int = Field(..., title="실행된 스케줄 수", example=5)
    failed_count: int = Field(..., title="실패한 스케줄 수", example=0)
    execution_time: datetime = Field(
        ..., title="실행 시간", example="2024-06-20T10:00:00Z"
    )
    details: List[Dict[str, Any]] = Field(
        default=[],
        title="실행 세부 정보",
        example=[
            {"schedule_id": 123, "status": "success", "message": "이메일 발송 완료"}
        ],
    )
