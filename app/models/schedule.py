import enum

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin


class ScheduleType(enum.Enum):
    """스케줄 타입 열거형"""

    EMAIL = "email"
    SMS = "sms"
    KAKAO = "kakao"


class ScheduleStatus(enum.Enum):
    """스케줄 상태 열거형"""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Schedule(Base, TimestampMixin):
    """예약 발송 스케줄 관리 테이블"""

    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True)
    api_key_id = Column(
        Integer, ForeignKey("api_keys.id"), nullable=False, comment="사용된 API 키 ID"
    )
    schedule_name = Column(String(100), nullable=False, comment="스케줄 이름")
    schedule_type = Column(Enum(ScheduleType), nullable=False, comment="스케줄 타입")

    # 스케줄 설정
    scheduled_at = Column(DateTime, nullable=False, comment="예약 실행 시간")
    timezone = Column(String(50), default="UTC", comment="시간대")

    # 발송 데이터
    payload = Column(Text, nullable=False, comment="발송 데이터 (JSON)")

    # 상태 관리
    status = Column(
        Enum(ScheduleStatus), default=ScheduleStatus.PENDING, comment="스케줄 상태"
    )
    executed_at = Column(DateTime, nullable=True, comment="실제 실행 시간")

    # 재시도 설정
    max_retry = Column(Integer, default=3, comment="최대 재시도 횟수")
    retry_count = Column(Integer, default=0, comment="현재 재시도 횟수")
    retry_interval = Column(Integer, default=300, comment="재시도 간격 (초)")

    # 결과
    result = Column(Text, nullable=True, comment="실행 결과 (JSON)")
    error_message = Column(Text, nullable=True, comment="오류 메시지")

    # 관계 설정
    api_key = relationship("ApiKey", back_populates="schedules")

    def __repr__(self):
        return f"<Schedule(id={self.id}, name='{self.schedule_name}', status='{self.status}')>"
