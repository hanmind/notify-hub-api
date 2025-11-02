from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin


class SmsLog(Base, TimestampMixin):
    """SMS 발송 로그 테이블"""

    __tablename__ = "sms_logs"

    id = Column(Integer, primary_key=True, index=True)
    api_key_id = Column(
        Integer, ForeignKey("api_keys.id"), nullable=False, comment="사용된 API 키 ID"
    )
    request_id = Column(
        String(100), unique=True, nullable=False, comment="요청 고유 ID"
    )

    # 발송 정보
    sender_phone = Column(String(20), nullable=False, comment="발송자 전화번호")
    recipient_phone = Column(String(20), nullable=False, comment="수신자 전화번호")

    # SMS 내용
    message = Column(Text, nullable=False, comment="SMS 메시지 내용")
    message_type = Column(
        String(10), nullable=False, default="SMS", comment="메시지 타입 (SMS, LMS, MMS)"
    )

    # 발송 상태
    status = Column(
        String(20),
        nullable=False,
        default="pending",
        comment="발송 상태 (pending, sent, failed)",
    )
    ncloud_request_id = Column(String(100), nullable=True, comment="NCloud 요청 ID")
    ncloud_response = Column(Text, nullable=True, comment="NCloud 응답 데이터 (JSON)")

    # 예약 발송
    scheduled_at = Column(DateTime, nullable=True, comment="예약 발송 시간")
    sent_at = Column(DateTime, nullable=True, comment="실제 발송 시간")

    # 오류 정보
    error_message = Column(Text, nullable=True, comment="오류 메시지")
    retry_count = Column(Integer, default=0, comment="재시도 횟수")

    # 관계 설정
    api_key = relationship("ApiKey", back_populates="sms_logs")

    def __repr__(self):
        return f"<SmsLog(id={self.id}, request_id='{self.request_id}', status='{self.status}')>"
