"""
SMS Router

Repository 패턴을 사용한 SMS 발송 관련 API
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

# Dependencies import (공통 사용)
## 의존성 함수들을 app/dependencies/로 이동
## -> 이제 공통으로 사용 가능한 의존성들을 import
from app.dependencies import get_api_key_id, get_sms_log_repository

# 데이터베이스 의존성
from app.models.base import get_db

# Repository import
from app.repositories.sms_log_repository import SmsLogRepository

# 라우터 인스턴스 생성
router = APIRouter(prefix="/sms", tags=["SMS"])


@router.get("/test")
def test_sms_service():
    """
    SMS 서비스 테스트

    Returns:
        dict: 테스트 결과
    """
    return {"message": "SMS service is ready (Repository pattern)"}


@router.post("/send")
async def send_sms(
    api_key_id: int = Depends(get_api_key_id),
    sms_repo: SmsLogRepository = Depends(get_sms_log_repository),
):
    """
    SMS 발송 (Repository 패턴 적용)

    X-API-Key 헤더를 통한 인증이 필요합니다.

    Returns:
        dict: 발송 결과
    """
    return {
        "message": "SMS send endpoint (Repository pattern)",
        "api_key_id": api_key_id,
        "note": "email_router와 동일한 인증 로직 재사용. 자세한 구현은 나중에 추가",
    }
