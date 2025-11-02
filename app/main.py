"""
FastAPI 메인 애플리케이션

Repository 패턴을 적용한 통합 알림 서비스의 FastAPI 엔트리포인트
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from app.exceptions import ApiError, http_exception_handler, api_exception_handler
from app.routers.email_router import router as email_router
from app.routers.sms_router import router as sms_router
from app.scheduler.local_scheduler import (
    get_scheduler_status,
    start_scheduler,
    stop_scheduler,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 라이프사이클 관리"""
    # 시작 시 실행
    print("🚀 Notification Service 시작 중...")

    # 로컬 스케줄러 시작 (환경변수로 제어)
    environment = os.getenv("ENVIRONMENT", "local")
    print(f"🌍 실행 환경: {environment}")

    if environment == "local":
        print("📅 로컬 스케줄러 시작 중...")
        await start_scheduler()
    else:
        print("🚫 배포 환경 - 로컬 스케줄러 비활성화 (AWS EventBridge 사용 예정)")

    print("✅ Notification Service 시작 완료!")

    yield

    # 종료 시 실행
    print("⏹️ Notification Service 종료 중...")
    await stop_scheduler()
    print("✅ Notification Service 종료 완료!")


# FastAPI 앱 인스턴스 생성
app = FastAPI(
    title="통합 알림 서비스 API",
    description="통합 알림 서비스 - Repository 패턴 적용",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI 경로
    redoc_url="/redoc",  # ReDoc 경로
    lifespan=lifespan,  # 라이프사이클 핸들러 등록
    exception_handlers={
        ApiError: api_exception_handler,  # 커스텀 에러 핸들러 등록
        HTTPException: http_exception_handler,  # 예상치 못한 HTTPException 처리
    },
    contact={
        "name": "API Support",
        "email": "support@example.com",
    },
)

# 라우터들을 앱에 등록
app.include_router(email_router, prefix="/api/v1")
app.include_router(sms_router, prefix="/api/v1")


# 기본 라우트 (루트 경로)
@app.get("/")
def read_root():
    """
    서비스 기본 정보 반환 (Repository 패턴 적용)
    """
    return {
        "service": "Notification Service API",
        "version": "0.3.0",
        "status": "running",
        "description": "통합 알림 서비스 (Repository 패턴)",
        "docs_url": "/docs",
        "architecture": "Model-Repository-Router-Schema-Service",
        "api_version": "v1",
        "environment": os.getenv("ENVIRONMENT", "local"),
        "scheduler_status": get_scheduler_status(),
        "endpoints": {
            # 이메일 API
            "email_test": "/api/v1/email/test",
            "email_send": "/api/v1/email/send",
            "email_bulk": "/api/v1/email/send-bulk",
            "email_status": "/api/v1/email/status/{request_id}",
            "email_list": "/api/v1/email/list/{request_id}",
            # 이메일 스케줄링
            "email_schedule_create": "/api/v1/email/schedule/create",
            "email_schedule_create_bulk": "/api/v1/email/schedule/create-bulk",
            "email_schedule_list": "/api/v1/email/schedule/list",
            "email_schedule_detail": "/api/v1/email/schedule/{schedule_id}",
            "email_schedule_cancel": "/api/v1/email/schedule/{schedule_id}",
            "email_schedule_execute": "/api/v1/email/schedule/execute-pending",
            # SMS API (향후 구현 예정)
            "sms_test": "/api/v1/sms/test",
            "sms_send": "/api/v1/sms/send",
            # 향후 구현 예정
            "sms_scheduling": "구현 예정 - /api/v1/sms/schedule/*",
            "kakao_scheduling": "구현 예정 - /api/v1/kakao/schedule/*",
            "slack_scheduling": "구현 예정 - /api/v1/slack/schedule/*",
            # 스케줄러 관리
            "scheduler_status": "/api/v1/scheduler/status",
        },
        "features": [
            "Repository 패턴으로 데이터 접근 계층 분리",
            "ORM 모델과 Alembic 마이그레이션",
            "타입 안전성과 의존성 주입",
            "확장 가능한 구조 설계",
            "발송 수단별 스케줄링 시스템",
            "API 키 기반 헤더 인증",
            "서비스별 로그 분리 및 추적",
            "로컬 개발환경용 자동 크론 스케줄러",
        ],
        "architecture_changes": {
            "v0.2.0": "Repository 패턴 도입, 통합 스케줄링",
            "v0.3.0": "발송 수단별 스케줄링으로 마이그레이션 완료",
            "v0.3.1": "로컬 크론 스케줄러 추가",
        },
        "links": [
            {
                "name": "통합 알림 서비스 API",
                "description": "통합 알림 서비스 (Repository 패턴)",
                "url": "https://github.com/yourusername/notification-service",
            }
        ],
    }


# 스케줄러 상태 조회 엔드포인트
@app.get("/api/v1/scheduler/status")
def get_local_scheduler_status():
    """
    로컬 스케줄러 상태 조회
    """
    return {
        "message": "로컬 스케줄러 상태 조회",
        "scheduler": get_scheduler_status(),
        "environment": os.getenv("ENVIRONMENT", "local"),
        "note": "로컬 개발환경에서만 스케줄러가 실행됩니다.",
    }
