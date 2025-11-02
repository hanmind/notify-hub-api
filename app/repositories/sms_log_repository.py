from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.sms_log import SmsLog

from .base import BaseRepository


class SmsLogRepository(BaseRepository[SmsLog]):
    """SMS 로그 Repository"""

    def __init__(self, db: Session):
        super().__init__(SmsLog, db)

    async def get_by_request_id(self, request_id: str) -> Optional[SmsLog]:
        """요청 ID로 SMS 로그 조회"""
        return self.db.query(SmsLog).filter(SmsLog.request_id == request_id).first()

    async def get_by_phone(self, phone: str) -> List[SmsLog]:
        """전화번호로 SMS 로그 조회"""
        return self.db.query(SmsLog).filter(SmsLog.recipient_phone == phone).all()
