"""
데이터베이스 관련 의존성

Repository와 Service 인스턴스 생성을 담당하는 의존성 함수들
"""

from fastapi import Depends
from sqlalchemy.orm import Session

from app.models.base import get_db
from app.repositories.email_log_repository import EmailLogRepository
from app.repositories.schedule_repository import ScheduleRepository
from app.repositories.sms_log_repository import SmsLogRepository
from app.services.email_service import EmailService


# Repository 의존성들
def get_email_log_repository(db: Session = Depends(get_db)) -> EmailLogRepository:
    """이메일 로그 Repository 의존성"""
    return EmailLogRepository(db)


def get_schedule_repository(db: Session = Depends(get_db)) -> ScheduleRepository:
    """스케줄 Repository 의존성"""
    return ScheduleRepository(db)


def get_sms_log_repository(db: Session = Depends(get_db)) -> SmsLogRepository:
    """SMS 로그 Repository 의존성"""
    return SmsLogRepository(db)


# Service 의존성들
def get_email_service(db: Session = Depends(get_db)) -> EmailService:
    """이메일 서비스 의존성"""
    return EmailService(db=db)
