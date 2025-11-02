from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.schedule import Schedule, ScheduleStatus, ScheduleType

from .base import BaseRepository


class ScheduleRepository(BaseRepository[Schedule]):
    """스케줄 Repository"""

    def __init__(self, db: Session):
        super().__init__(Schedule, db)

    def get_pending_schedules_by_time(self, current_time: datetime) -> List[Schedule]:
        """현재 시간 기준으로 실행 대기 중인 스케줄 조회"""
        return (
            self.db.query(Schedule)
            .filter(
                Schedule.scheduled_at <= current_time,
                Schedule.status == ScheduleStatus.PENDING,
            )
            .all()
        )

    def get_pending_schedules_by_time_and_type(
        self, current_time: datetime, schedule_type: ScheduleType
    ) -> List[Schedule]:
        """현재 시간 기준으로 특정 타입의 실행 대기 중인 스케줄 조회"""
        return (
            self.db.query(Schedule)
            .filter(
                Schedule.scheduled_at <= current_time,
                Schedule.status == ScheduleStatus.PENDING,
                Schedule.schedule_type == schedule_type,
            )
            .all()
        )

    def get_by_status(self, status: ScheduleStatus) -> List[Schedule]:
        """상태별 스케줄 조회"""
        return self.db.query(Schedule).filter(Schedule.status == status).all()

    def update_status(
        self,
        schedule_id: int,
        status: ScheduleStatus,
        executed_at: Optional[datetime] = None,
        result: Optional[str] = None,
    ) -> Schedule:
        """스케줄 상태 업데이트"""
        schedule = self.db.query(Schedule).filter(Schedule.id == schedule_id).first()
        if schedule:
            schedule.status = status
            if executed_at:
                schedule.executed_at = executed_at
            if result:
                schedule.result = result
            schedule.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(schedule)
        return schedule

    def handle_failure(self, schedule_id: int, error_message: str) -> Schedule:
        """스케줄 실패 처리 (재시도 로직 포함)"""
        schedule = self.db.query(Schedule).filter(Schedule.id == schedule_id).first()
        if schedule:
            schedule.retry_count += 1
            schedule.error_message = error_message
            schedule.updated_at = datetime.utcnow()

            # 최대 재시도 횟수 초과 시 실패 처리
            if schedule.retry_count >= schedule.max_retry:
                schedule.status = ScheduleStatus.FAILED
            else:
                # 재시도 대기 상태로 변경 (다음 크론에서 다시 시도)
                schedule.status = ScheduleStatus.PENDING
                # 재시도 간격만큼 스케줄 시간 연기
                schedule.scheduled_at = datetime.utcnow().replace(
                    second=0, microsecond=0
                ) + timedelta(seconds=schedule.retry_interval)

            self.db.commit()
            self.db.refresh(schedule)
        return schedule

    def create(
        self,
        api_key_id: int,
        schedule_name: str,
        schedule_type: ScheduleType,
        scheduled_at: datetime,
        payload: str,
        timezone: str = "UTC",
        max_retry: int = 3,
        retry_interval: int = 300,
    ) -> Schedule:
        """새 스케줄 생성"""
        schedule = Schedule(
            api_key_id=api_key_id,
            schedule_name=schedule_name,
            schedule_type=schedule_type,
            scheduled_at=scheduled_at,
            payload=payload,
            timezone=timezone,
            max_retry=max_retry,
            retry_interval=retry_interval,
            status=ScheduleStatus.PENDING,
            retry_count=0,
        )

        self.db.add(schedule)
        self.db.commit()
        self.db.refresh(schedule)
        return schedule

    def get_list(
        self,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Schedule]:
        """조건별 스케줄 목록 조회"""
        query = self.db.query(Schedule)

        if filters:
            if "status" in filters:
                query = query.filter(Schedule.status == filters["status"])
            if "schedule_type" in filters:
                query = query.filter(Schedule.schedule_type == filters["schedule_type"])
            if "api_key_id" in filters:
                query = query.filter(Schedule.api_key_id == filters["api_key_id"])

        return (
            query.order_by(Schedule.created_at.desc()).offset(offset).limit(limit).all()
        )

    def get_by_filters(
        self,
        filters: Dict[str, Any],
        limit: int = 100,
        offset: int = 0,
    ) -> List[Schedule]:
        """필터 조건으로 스케줄 목록 조회"""
        query = self.db.query(Schedule)

        if "status" in filters:
            query = query.filter(Schedule.status == filters["status"])
        if "schedule_type" in filters:
            query = query.filter(Schedule.schedule_type == filters["schedule_type"])
        if "api_key_id" in filters:
            query = query.filter(Schedule.api_key_id == filters["api_key_id"])

        return (
            query.order_by(Schedule.created_at.desc()).offset(offset).limit(limit).all()
        )

    def count_by_filters(self, filters: Dict[str, Any]) -> int:
        """필터 조건으로 스케줄 개수 조회"""
        query = self.db.query(Schedule)

        if "status" in filters:
            query = query.filter(Schedule.status == filters["status"])
        if "schedule_type" in filters:
            query = query.filter(Schedule.schedule_type == filters["schedule_type"])
        if "api_key_id" in filters:
            query = query.filter(Schedule.api_key_id == filters["api_key_id"])

        return query.count()

    def get_retry_pending_schedules(self, current_time: datetime) -> List[Schedule]:
        """재시도 대기 중인 스케줄 조회"""
        return (
            self.db.query(Schedule)
            .filter(
                Schedule.scheduled_at <= current_time,
                Schedule.status == ScheduleStatus.PENDING,
                Schedule.retry_count > 0,
                Schedule.retry_count < Schedule.max_retry,
            )
            .all()
        )
