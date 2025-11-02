from datetime import datetime
from typing import List, Optional

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.models.email_log import EmailLog

from .base import BaseRepository


class EmailLogRepository(BaseRepository[EmailLog]):
    """이메일 로그 Repository - 이메일 관련 특화 쿼리 제공"""

    def __init__(self, db: Session):
        super().__init__(EmailLog, db)

    async def get_by_request_id(self, request_id: str) -> Optional[EmailLog]:
        """요청 ID로 이메일 로그 조회"""
        return self.db.query(EmailLog).filter(EmailLog.request_id == request_id).first()

    async def get_by_status(
        self, status: str, skip: int = 0, limit: int = 100
    ) -> List[EmailLog]:
        """상태별 이메일 로그 조회"""
        return (
            self.db.query(EmailLog)
            .filter(EmailLog.status == status)
            .offset(skip)
            .limit(limit)
            .all()
        )

    async def get_by_api_key(
        self, api_key_id: int, skip: int = 0, limit: int = 100
    ) -> List[EmailLog]:
        """API 키별 이메일 로그 조회"""
        return (
            self.db.query(EmailLog)
            .filter(EmailLog.api_key_id == api_key_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    async def get_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        skip: int = 0,
        limit: int = 100,
    ) -> List[EmailLog]:
        """날짜 범위별 이메일 로그 조회"""
        return (
            self.db.query(EmailLog)
            .filter(
                and_(
                    EmailLog.created_at >= start_date,
                    EmailLog.created_at <= end_date,
                )
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    async def get_scheduled_emails(self, scheduled_time: datetime) -> List[EmailLog]:
        """예약 발송 대상 이메일 조회"""
        return (
            self.db.query(EmailLog)
            .filter(
                and_(
                    EmailLog.scheduled_at <= scheduled_time,
                    EmailLog.status == "pending",
                )
            )
            .all()
        )

    async def get_failed_emails(self, max_retry: int = 3) -> List[EmailLog]:
        """재시도 가능한 실패 이메일 조회"""
        return (
            self.db.query(EmailLog)
            .filter(
                and_(
                    EmailLog.status == "failed",
                    EmailLog.retry_count < max_retry,
                )
            )
            .all()
        )

    async def update_status(
        self, request_id: str, status: str, **kwargs
    ) -> Optional[EmailLog]:
        """이메일 상태 업데이트"""
        email_log = await self.get_by_request_id(request_id)
        if email_log:
            update_data = {"status": status, **kwargs}
            return await self.update(email_log, update_data)
        return None

    async def get_statistics(self, start_date: datetime, end_date: datetime) -> dict:
        """기간별 이메일 발송 통계"""
        from sqlalchemy import func

        result = (
            self.db.query(
                EmailLog.status,
                func.count(EmailLog.id).label("count"),
            )
            .filter(
                and_(
                    EmailLog.created_at >= start_date,
                    EmailLog.created_at <= end_date,
                )
            )
            .group_by(EmailLog.status)
            .all()
        )

        return {row.status: row.count for row in result}
