import enum

from sqlalchemy import Boolean, Column, Enum, Integer, String, Text

from .base import Base, TimestampMixin


class TemplateType(enum.Enum):
    """템플릿 타입 열거형"""

    EMAIL = "email"
    SMS = "sms"
    KAKAO = "kakao"


class Template(Base, TimestampMixin):
    """메시지 템플릿 관리 테이블"""

    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, index=True)
    template_name = Column(String(100), nullable=False, comment="템플릿 이름")
    template_type = Column(Enum(TemplateType), nullable=False, comment="템플릿 타입")

    # 템플릿 내용
    subject = Column(String(500), nullable=True, comment="제목 (이메일용)")
    body_text = Column(Text, nullable=True, comment="텍스트 본문")
    body_html = Column(Text, nullable=True, comment="HTML 본문 (이메일용)")

    # 템플릿 변수
    variables = Column(Text, nullable=True, comment="템플릿 변수 목록 (JSON)")

    # 상태
    is_active = Column(Boolean, default=True, nullable=False, comment="활성화 여부")
    description = Column(Text, nullable=True, comment="템플릿 설명")

    # 카테고리
    category = Column(String(50), nullable=True, comment="템플릿 카테고리")

    def __repr__(self):
        return f"<Template(id={self.id}, name='{self.template_name}', type='{self.template_type}')>"
