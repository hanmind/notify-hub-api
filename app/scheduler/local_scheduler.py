"""
로컬 크론 스케줄러

APScheduler를 사용하여 로컬 개발환경에서
예약된 이메일을 자동으로 실행하는 스케줄러
"""

import asyncio
import logging
import os
from datetime import datetime
from typing import Optional

import httpx
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

# 로거 설정
logger = logging.getLogger(__name__)


class LocalScheduler:
    """로컬 개발환경용 크론 스케줄러"""

    def __init__(self):
        self.scheduler: Optional[AsyncIOScheduler] = None
        self.running = False
        self.base_url = "http://localhost:8000"  # FastAPI 서버 주소

        # ENVIRONMENT 환경변수로 스케줄러 활성화 여부 결정
        environment = os.getenv("ENVIRONMENT", "local")
        self.enabled = environment == "local"
        self.interval_minutes = int(os.getenv("SCHEDULER_INTERVAL_MINUTES", "60"))
        self.timezone = os.getenv("SCHEDULER_TIMEZONE", "Asia/Seoul")

        logger.info(
            f"로컬 스케줄러 초기화 - 환경: {environment}, 활성화: {self.enabled}, 간격: {self.interval_minutes}분"
        )

    async def start(self):
        """스케줄러 시작"""
        if not self.enabled:
            logger.info("로컬 스케줄러가 비활성화되어 있습니다.")
            return

        if self.running:
            logger.warning("스케줄러가 이미 실행 중입니다.")
            return

        try:
            # AsyncIOScheduler 생성
            self.scheduler = AsyncIOScheduler(timezone=self.timezone)

            # 이메일 스케줄 실행 작업 등록
            self.scheduler.add_job(
                func=self.execute_email_schedules,
                trigger=IntervalTrigger(minutes=self.interval_minutes),
                id="email_schedule_executor",
                name="이메일 스케줄 실행기",
                replace_existing=True,
                max_instances=1,  # 동시 실행 방지
            )

            # 스케줄러 시작
            self.scheduler.start()
            self.running = True

            logger.info(f"로컬 스케줄러 시작 완료 - {self.interval_minutes}분마다 실행")

        except Exception as e:
            logger.error(f"스케줄러 시작 실패: {str(e)}")
            raise

    async def stop(self):
        """스케줄러 중지"""
        if not self.running or not self.scheduler:
            return

        try:
            self.scheduler.shutdown(wait=True)
            self.running = False
            logger.info("로컬 스케줄러 중지 완료")

        except Exception as e:
            logger.error(f"스케줄러 중지 실패: {str(e)}")

    async def execute_email_schedules(self):
        """예약된 이메일 스케줄 실행"""
        try:
            current_time = datetime.now()
            logger.info(
                f"이메일 스케줄 실행 시작 - {current_time.strftime('%Y-%m-%d %H:%M:%S')}"
            )

            # FastAPI 서버의 execute-pending 엔드포인트 호출
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/email/schedule/execute-pending",
                    headers={"Content-Type": "application/json"},
                )

                if response.status_code == 200:
                    result = response.json()
                    executed_count = result.get("executed_count", 0)
                    failed_count = result.get("failed_count", 0)

                    if executed_count > 0 or failed_count > 0:
                        logger.info(
                            f"이메일 스케줄 실행 완료 - "
                            f"성공: {executed_count}, 실패: {failed_count}"
                        )
                else:
                    logger.error(
                        f"이메일 스케줄 실행 실패 - HTTP {response.status_code}"
                    )

        except httpx.TimeoutException:
            logger.error("이메일 스케줄 실행 타임아웃")
        except httpx.ConnectError:
            logger.error(
                "FastAPI 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요."
            )
        except Exception as e:
            logger.error(f"이메일 스케줄 실행 중 오류: {str(e)}")

    def get_status(self) -> dict:
        """스케줄러 상태 반환"""
        if not self.scheduler:
            return {
                "running": False,
                "enabled": self.enabled,
                "message": "스케줄러가 초기화되지 않았습니다.",
            }

        jobs = []
        if self.scheduler.get_jobs():
            for job in self.scheduler.get_jobs():
                jobs.append(
                    {
                        "id": job.id,
                        "name": job.name,
                        "next_run": (
                            job.next_run_time.isoformat() if job.next_run_time else None
                        ),
                    }
                )

        return {
            "running": self.running,
            "enabled": self.enabled,
            "interval_minutes": self.interval_minutes,
            "timezone": self.timezone,
            "jobs": jobs,
            "message": (
                "스케줄러가 정상 실행 중입니다."
                if self.running
                else "스케줄러가 중지되었습니다."
            ),
        }


# 전역 스케줄러 인스턴스
local_scheduler = LocalScheduler()


async def start_scheduler():
    """스케줄러 시작 (FastAPI 시작 시 호출)"""
    await local_scheduler.start()


async def stop_scheduler():
    """스케줄러 중지 (FastAPI 종료 시 호출)"""
    await local_scheduler.stop()


def get_scheduler_status() -> dict:
    """스케줄러 상태 조회"""
    return local_scheduler.get_status()
