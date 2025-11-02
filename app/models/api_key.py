from sqlalchemy import Boolean, Column, Integer, String, Text
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin


class ApiKey(Base, TimestampMixin):
    """API 키 관리 테이블"""

    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    key_name = Column(String(100), nullable=False, comment="API 키 이름")
    api_key = Column(String(255), unique=True, nullable=False, comment="API 키 값")
    service_name = Column(
        String(50), nullable=False, comment="서비스명 (service_a, service_b, service_c)"
    )
    is_active = Column(Boolean, default=True, nullable=False, comment="활성화 여부")
    allowed_ips = Column(Text, nullable=True, comment="허용된 IP 주소 목록 (JSON 배열)")
    description = Column(Text, nullable=True, comment="API 키 설명")

    # 관계 설정
    email_logs = relationship("EmailLog", back_populates="api_key")
    sms_logs = relationship("SmsLog", back_populates="api_key")
    schedules = relationship("Schedule", back_populates="api_key")

    def __repr__(self):
        return f"<ApiKey(id={self.id}, key_name='{self.key_name}', service_name='{self.service_name}')>"
