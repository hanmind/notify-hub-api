from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin


class EmailLog(Base, TimestampMixin):
    """이메일 발송 로그 테이블"""

    __tablename__ = "email_logs"

    id = Column(Integer, primary_key=True, index=True)
    api_key_id = Column(
        Integer, ForeignKey("api_keys.id"), nullable=False, comment="사용된 API 키 ID"
    )
    request_id = Column(
        String(100), unique=True, nullable=False, comment="요청 고유 ID"
    )

    # 발송 정보
    sender_email = Column(String(255), nullable=False, comment="발송자 이메일")
    sender_name = Column(String(100), nullable=True, comment="발송자 이름")
    recipient_email = Column(String(255), nullable=False, comment="수신자 이메일")
    recipient_name = Column(String(100), nullable=True, comment="수신자 이름")

    # 이메일 내용
    subject = Column(String(500), nullable=False, comment="이메일 제목")
    body_text = Column(Text, nullable=True, comment="텍스트 본문")
    body_html = Column(Text, nullable=True, comment="HTML 본문")

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

    # 첨부파일
    has_attachments = Column(Boolean, default=False, comment="첨부파일 여부")
    attachment_info = Column(Text, nullable=True, comment="첨부파일 정보 (JSON)")

    # 오류 정보
    error_message = Column(Text, nullable=True, comment="오류 메시지")
    retry_count = Column(Integer, default=0, comment="재시도 횟수")

    # 관계 설정
    api_key = relationship("ApiKey", back_populates="email_logs")

    def __repr__(self):
        return f"<EmailLog(id={self.id}, request_id='{self.request_id}', status='{self.status}')>"
