"""
이메일 Router

Repository 패턴을 사용한 이메일 발송 관련 API
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, Header, HTTPException
from fastapi.params import Query
from sqlalchemy import text
from sqlalchemy.orm import Session

# Dependencies import
## 의존성 함수들을 app/dependencies/로 이동
## -> 이제 공통으로 사용 가능한 의존성들을 import
from app.dependencies import (
    get_api_key_id,
    get_api_key_repository,
    get_email_log_repository,
    get_email_service,
    get_schedule_repository,
)

# 커스텀 예외 import
from app.exceptions import ErrorCodes, ApiError

# 데이터베이스 의존성
from app.models.base import get_db

# 모델 import
from app.models.schedule import Schedule, ScheduleStatus, ScheduleType

# Repository import
from app.repositories.api_key_repository import ApiKeyRepository
from app.repositories.email_log_repository import EmailLogRepository
from app.repositories.schedule_repository import ScheduleRepository

# 스키마 import
from app.schemas.common import PaginationParams, ScheduleFilterParams
from app.schemas.email import (  # 스케줄링 스키마
    BulkEmailRequest,
    BulkEmailScheduleRequest,
    EmailListResponse,
    EmailRequest,
    EmailResponse,
    EmailScheduleExecuteResponse,
    EmailScheduleListResponse,
    EmailScheduleRequest,
    EmailScheduleResponse,
    EmailStatusResponse,
)

# 서비스 import
from app.services.email_service import EmailService

# 로거 설정
logger = logging.getLogger(__name__)

# 라우터 인스턴스 생성
router = APIRouter(prefix="/email", tags=["Email"])


# 테스트용 엔드포인트
# @router.get("/test-http-error")
# def test_http_error():
#     """
#     HTTPException 핸들러 테스트용 엔드포인트

#     예상치 못한 HTTPException이 발생했을 때 핸들러가 제대로 작동하는지 확인
#     """
#     raise HTTPException(status_code=500, detail="의도적으로 발생시킨 테스트 에러입니다")


# @router.get("/test")
# def test_email_service(email_service: EmailService = Depends(get_email_service)):
#     """
#     이메일 서비스 테스트

#     Returns:
#         dict: 테스트 결과
#     """
#     return email_service.health_check()


# @router.get("/db-test")
# def test_db_connection(db: Session = Depends(get_db)):
#     """
#     DB 연결 테스트 (1단계: 기본 연결)

#     Returns:
#         dict: DB 연결 테스트 결과
#     """
#     try:
#         # 가장 간단한 쿼리 실행
#         result = db.execute(text("SELECT 1 as test_value")).fetchone()
#         return {
#             "success": True,
#             "message": "DB 연결 성공",
#             "test_query_result": result[0] if result else None,
#             "timestamp": datetime.utcnow().isoformat(),
#         }
#     except Exception as e:
#         return {
#             "success": False,
#             "message": f"DB 연결 실패: {str(e)}",
#             "error_type": type(e).__name__,
#             "timestamp": datetime.utcnow().isoformat(),
#         }


# @router.get("/db-test-tables")
# def test_db_tables(db: Session = Depends(get_db)):
#     """
#     DB 테이블 존재 확인 (2단계: 테이블 조회)

#     Returns:
#         dict: 테이블 존재 확인 결과
#     """
#     tables_to_check = ["api_keys", "email_logs", "schedules", "templates", "sms_logs"]
#     results = {}

#     try:
#         for table in tables_to_check:
#             try:
#                 result = db.execute(text(f"SELECT COUNT(*) FROM {table}")).fetchone()
#                 results[table] = {"exists": True, "count": result[0] if result else 0}
#             except Exception as e:
#                 results[table] = {"exists": False, "error": str(e)}

#         return {
#             "success": True,
#             "message": "테이블 조회 완료",
#             "tables": results,
#             "timestamp": datetime.utcnow().isoformat(),
#         }
#     except Exception as e:
#         return {
#             "success": False,
#             "message": f"테이블 조회 실패: {str(e)}",
#             "error_type": type(e).__name__,
#             "timestamp": datetime.utcnow().isoformat(),
#         }


# @router.get("/db-test-apikeys")
# async def test_api_keys_table(
#     api_key_repo: ApiKeyRepository = Depends(get_api_key_repository),
# ):
#     """
#     API 키 테이블 조회 테스트 (3단계: Repository 패턴)

#     Returns:
#         dict: API 키 테이블 조회 결과
#     """
#     try:
#         # Repository를 통한 활성 API 키 목록 조회
#         api_keys = await api_key_repo.get_active_keys()

#         return {
#             "success": True,
#             "message": "API 키 테이블 조회 성공",
#             "api_key_count": len(api_keys),
#             "api_keys": [
#                 {
#                     "id": key.id,
#                     "key_name": key.key_name,
#                     "service_name": key.service_name,
#                     "is_active": key.is_active,
#                     "api_key_preview": f"{key.api_key[:8]}..." if key.api_key else None,
#                 }
#                 for key in api_keys
#             ],
#             "timestamp": datetime.utcnow().isoformat(),
#         }
#     except Exception as e:
#         return {
#             "success": False,
#             "message": f"API 키 테이블 조회 실패: {str(e)}",
#             "error_type": type(e).__name__,
#             "timestamp": datetime.utcnow().isoformat(),
#         }


@router.post("/send", response_model=EmailResponse)
async def send_email(
    request: EmailRequest,
    api_key_id: int = Depends(get_api_key_id),  # 헤더에서 API 키 인증
    email_service: EmailService = Depends(get_email_service),
    email_repo: EmailLogRepository = Depends(get_email_log_repository),
):
    """
    단일 이메일 발송 (로그 저장 포함)

    Args:
        request: 이메일 발송 요청 데이터
        api_key_id: 헤더 인증을 통해 얻은 API 키 ID

    Returns:
        EmailResponse: 발송 결과
    """
    # 이메일 서비스로 발송 (로그 저장 포함)
    result = await email_service.send_single_email(request, api_key_id=api_key_id)

    return EmailResponse(
        success=result["success"],
        message=result["message"],
        request_id=result["request_id"],
        recipient_count=result["recipient_count"],
    )


@router.post("/send-bulk", response_model=EmailResponse)
async def send_bulk_email(
    request: BulkEmailRequest,
    api_key_id: int = Depends(get_api_key_id),  # 헤더에서 API 키 인증
    email_service: EmailService = Depends(get_email_service),
    email_repo: EmailLogRepository = Depends(get_email_log_repository),
):
    """
    대량 이메일 발송 (Repository 패턴 적용)

    Args:
        request: 대량 이메일 발송 요청 데이터
        api_key_id: 헤더 인증을 통해 얻은 API 키 ID

    Returns:
        EmailResponse: 발송 결과
    """
    result = await email_service.send_bulk_email(request, api_key_id=api_key_id)
    return EmailResponse(
        success=result["success"],
        message=result["message"],
        request_id=result["request_id"],
        recipient_count=result["recipient_count"],
    )


@router.get("/status/{mail_id}", response_model=EmailStatusResponse)
async def get_email_status(
    mail_id: str,
    api_key_id: int = Depends(get_api_key_id),  # 헤더에서 API 키 인증
    email_service: EmailService = Depends(get_email_service),
    email_repo: EmailLogRepository = Depends(get_email_log_repository),
):
    """
    이메일 발송 상태 조회 (Repository 패턴 적용)

    Args:
        mail_id: NCloud에서 반환한 메일 ID (mailId)
        api_key_id: 헤더 인증을 통해 얻은 API 키 ID

    Returns:
        EmailStatusResponse: 상태 조회 결과
    """
    # 1. NCloud에서 상태 조회
    result = await email_service.get_email_status(mail_id)

    # 2. Repository를 통해 로컬 DB 상태 업데이트 (향후 구현)
    # await email_repo.update_status(mail_id, result["status"])

    return EmailStatusResponse(
        request_id=result["mail_id"],
        status=result["status"],
        details=result["details"],
    )


@router.get("/list/{request_id}", response_model=EmailListResponse)
async def get_mail_list(
    request_id: str,
    params: PaginationParams = Query(),
    api_key_id: int = Depends(get_api_key_id),  # 헤더에서 API 키 인증
    email_service: EmailService = Depends(get_email_service),
    email_repo: EmailLogRepository = Depends(get_email_log_repository),
):
    """
    이메일 요청 목록 조회 (Repository 패턴 적용)

    Args:
        request_id: 특정 요청 ID (필수)
        params: 페이지네이션 파라미터 (페이지 번호, 크기)
        api_key_id: 헤더 인증을 통해 얻은 API 키 ID

    Returns:
        EmailListResponse: 메일 목록 조회 결과
    """
    # 1. NCloud에서 목록 조회
    result = await email_service.get_mail_list(request_id, params.page, params.size)

    # 2. Repository를 통해 로컬 DB에서도 조회 (향후 구현)
    # local_logs = await email_repo.get_by_request_id(request_id)

    return EmailListResponse(
        request_id=result["request_id"],
        page=result["page"],
        size=result["size"],
        status=result["status"],
        details=result["details"],
    )


@router.post("/schedule/create", response_model=EmailScheduleResponse)
async def create_email_schedule(
    request: EmailScheduleRequest,
    api_key_id: int = Depends(get_api_key_id),
    schedule_repo: ScheduleRepository = Depends(get_schedule_repository),
    email_service: EmailService = Depends(get_email_service),
):
    """
    이메일 스케줄 생성

    Args:
        request: 이메일 스케줄 생성 요청
        api_key_id: API 키 ID

    Returns:
        EmailScheduleResponse: 스케줄 생성 결과
    """
    # API 키 기반 발송자 자동 선택 (요청에서 지정하지 않은 경우)
    sender_address = request.sender_address
    if not sender_address:
        sender_address = email_service._get_sender_email_by_api_key(api_key_id)
        logger.info(f"스케줄 생성 시 API 키 기반 발송자 자동 선택: {sender_address}")

    # 페이로드 생성 (이메일 발송에 필요한 데이터)
    payload = {
        "to_email": request.to_email,
        "to_name": request.to_name,
        "subject": request.subject,
        "html_body": request.html_body,
        "sender_address": sender_address,
        "template_id": request.template_id,
        "template_variables": request.template_variables,
    }

    # 스케줄 생성
    schedule = schedule_repo.create(
        api_key_id=api_key_id,
        schedule_name=request.schedule_name,
        schedule_type=ScheduleType.EMAIL,
        scheduled_at=request.scheduled_at,
        payload=json.dumps(payload),
        timezone=request.timezone,
        max_retry=request.max_retry,
        retry_interval=request.retry_interval,
    )

    logger.info(f"이메일 스케줄 생성 완료: {schedule.id}")

    return EmailScheduleResponse(
        success=True,
        message="이메일 스케줄이 성공적으로 생성되었습니다",
        schedule_id=schedule.id,
        schedule_name=schedule.schedule_name,
        scheduled_at=schedule.scheduled_at,
        status=schedule.status.value,
        created_at=schedule.created_at,
    )


@router.post("/schedule/create-bulk", response_model=EmailScheduleResponse)
async def create_bulk_email_schedule(
    request: BulkEmailScheduleRequest,
    api_key_id: int = Depends(get_api_key_id),
    schedule_repo: ScheduleRepository = Depends(get_schedule_repository),
    email_service: EmailService = Depends(get_email_service),
):
    """
    대량 이메일 스케줄 생성

    Args:
        request: 대량 이메일 스케줄 생성 요청
        api_key_id: API 키 ID

    Returns:
        EmailScheduleResponse: 스케줄 생성 결과
    """
    # API 키 기반 발송자 자동 선택 (요청에서 지정하지 않은 경우)
    sender_address = request.sender_address
    if not sender_address:
        sender_address = email_service._get_sender_email_by_api_key(api_key_id)
        logger.info(
            f"대량 스케줄 생성 시 API 키 기반 발송자 자동 선택: {sender_address}"
        )

    # 페이로드 생성
    payload = {
        "recipients": [{"email": r.email, "name": r.name} for r in request.recipients],
        "subject": request.subject,
        "html_body": request.html_body,
        "sender_address": sender_address,
        "template_id": request.template_id,
        "template_variables": request.template_variables,
        "is_bulk": True,
    }

    # 스케줄 생성
    schedule = schedule_repo.create(
        api_key_id=api_key_id,
        schedule_name=request.schedule_name,
        schedule_type=ScheduleType.EMAIL,
        scheduled_at=request.scheduled_at,
        payload=json.dumps(payload),
        timezone=request.timezone,
        max_retry=request.max_retry,
        retry_interval=request.retry_interval,
    )

    logger.info(f"대량 이메일 스케줄 생성 완료: {schedule.id}")

    return EmailScheduleResponse(
        success=True,
        message=f"대량 이메일 스케줄이 성공적으로 생성되었습니다 (수신자 {len(request.recipients)}명)",
        schedule_id=schedule.id,
        schedule_name=schedule.schedule_name,
        scheduled_at=schedule.scheduled_at,
        status=schedule.status.value,
        created_at=schedule.created_at,
    )


@router.get("/schedule/list", response_model=EmailScheduleListResponse)
async def list_email_schedules(
    params: ScheduleFilterParams = Query(),
    api_key_id: int = Depends(get_api_key_id),
    schedule_repo: ScheduleRepository = Depends(get_schedule_repository),
):
    """
    이메일 스케줄 목록 조회

    Args:
        status: 스케줄 상태 필터 (pending, processing, completed, failed, cancelled)
        limit: 조회할 최대 개수
        offset: 조회 시작 위치
        api_key_id: API 키 ID

    Returns:
        EmailScheduleListResponse: 스케줄 목록
    """
    # 필터 조건 설정
    filters = {"schedule_type": ScheduleType.EMAIL, "api_key_id": api_key_id}
    if params.status:
        filters["status"] = ScheduleStatus(params.status)

    # 스케줄 목록 조회
    schedules = schedule_repo.get_by_filters(
        filters, limit=params.limit, offset=params.offset
    )
    total_count = schedule_repo.count_by_filters(filters)

    # 응답 데이터 구성
    schedule_list = []
    for schedule in schedules:
        schedule_data = {
            "schedule_id": schedule.id,
            "schedule_name": schedule.schedule_name,
            "scheduled_at": schedule.scheduled_at.isoformat(),
            "status": schedule.status.value,
            "created_at": schedule.created_at.isoformat(),
            "executed_at": (
                schedule.executed_at.isoformat() if schedule.executed_at else None
            ),
            "retry_count": schedule.retry_count,
            "error_message": schedule.error_message,
        }
        schedule_list.append(schedule_data)

    return EmailScheduleListResponse(
        schedules=schedule_list,
        total_count=total_count,
        page=params.offset // params.limit,
        size=params.limit,
    )


@router.get("/schedule/{schedule_id}")
async def get_email_schedule(
    schedule_id: int,
    api_key_id: int = Depends(get_api_key_id),
    schedule_repo: ScheduleRepository = Depends(get_schedule_repository),
):
    """
    이메일 스케줄 상세 조회

    Args:
        schedule_id: 스케줄 ID
        api_key_id: API 키 ID

    Returns:
        dict: 스케줄 상세 정보
    """
    schedule = schedule_repo.get_by_id(schedule_id)

    if not schedule:
        raise ApiError(
            message="스케줄을 찾을 수 없습니다",
            error_code=ErrorCodes.SCHEDULE_NOT_FOUND,
            status_code=404,
        )

    # API 키 권한 확인
    if schedule.api_key_id != api_key_id:
        raise ApiError(
            message="접근 권한이 없습니다",
            error_code=ErrorCodes.SCHEDULE_ACCESS_DENIED,
            status_code=403,
        )

    # 이메일 스케줄인지 확인
    if schedule.schedule_type != ScheduleType.EMAIL:
        raise ApiError(
            message="이메일 스케줄이 아닙니다",
            error_code=ErrorCodes.SCHEDULE_INVALID_TYPE,
            status_code=400,
        )

    return {
        "schedule_id": schedule.id,
        "schedule_name": schedule.schedule_name,
        "schedule_type": schedule.schedule_type.value,
        "scheduled_at": schedule.scheduled_at.isoformat(),
        "timezone": schedule.timezone,
        "status": schedule.status.value,
        "payload": json.loads(schedule.payload),
        "max_retry": schedule.max_retry,
        "retry_count": schedule.retry_count,
        "retry_interval": schedule.retry_interval,
        "created_at": schedule.created_at.isoformat(),
        "executed_at": (
            schedule.executed_at.isoformat() if schedule.executed_at else None
        ),
        "result": json.loads(schedule.result) if schedule.result else None,
        "error_message": schedule.error_message,
    }


@router.delete("/schedule/{schedule_id}")
async def cancel_email_schedule(
    schedule_id: int,
    api_key_id: int = Depends(get_api_key_id),
    schedule_repo: ScheduleRepository = Depends(get_schedule_repository),
):
    """
    이메일 스케줄 취소

    Args:
        schedule_id: 스케줄 ID
        api_key_id: API 키 ID

    Returns:
        dict: 취소 결과
    """
    try:
        schedule = schedule_repo.get_by_id(schedule_id)

        if not schedule:
            raise ApiError(
                message="스케줄을 찾을 수 없습니다",
                error_code=ErrorCodes.SCHEDULE_NOT_FOUND,
                status_code=404,
            )

        # API 키 권한 확인
        if schedule.api_key_id != api_key_id:
            raise ApiError(
                message="접근 권한이 없습니다",
                error_code=ErrorCodes.SCHEDULE_ACCESS_DENIED,
                status_code=403,
            )

        # 이메일 스케줄인지 확인
        if schedule.schedule_type != ScheduleType.EMAIL:
            raise ApiError(
                message="이메일 스케줄이 아닙니다",
                error_code=ErrorCodes.SCHEDULE_INVALID_TYPE,
                status_code=400,
            )

        # 취소 가능한 상태인지 확인
        if schedule.status not in [ScheduleStatus.PENDING]:
            raise ApiError(
                message=f"취소할 수 없는 상태입니다: {schedule.status.value}",
                error_code=ErrorCodes.SCHEDULE_ALREADY_EXECUTED,
                status_code=400,
            )

        # 스케줄 취소
        schedule_repo.update_status(schedule_id, ScheduleStatus.CANCELLED)

        logger.info(f"이메일 스케줄 취소 완료: {schedule_id}")

        return {
            "message": "이메일 스케줄이 취소되었습니다",
            "schedule_id": schedule_id,
            "cancelled_at": datetime.utcnow().isoformat(),
        }

    except ApiError:
        raise
    except Exception as e:
        logger.error(f"이메일 스케줄 취소 실패: {str(e)}")
        raise ApiError(
            message=f"스케줄 취소 실패: {str(e)}",
            error_code=ErrorCodes.SCHEDULE_CANCEL_FAILED,
            status_code=400,
        )


@router.post("/schedule/execute-pending", response_model=EmailScheduleExecuteResponse)
async def execute_pending_email_schedules(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    예약된 이메일 스케줄 실행 (EventBridge에서 호출)

    AWS EventBridge → API Gateway → 이 엔드포인트
    매분 실행되어 현재 시간에 실행되어야 할 이메일 스케줄들을 처리
    """
    try:
        schedule_repo = ScheduleRepository(db)
        current_time = datetime.utcnow()

        # 실행 대기 중인 이메일 스케줄들 조회
        pending_schedules = schedule_repo.get_pending_schedules_by_time_and_type(
            current_time, ScheduleType.EMAIL
        )

        executed_count = 0
        failed_count = 0
        execution_details = []

        for schedule in pending_schedules:
            try:
                # 백그라운드에서 실행
                background_tasks.add_task(execute_single_email_schedule, schedule, db)
                executed_count += 1
                execution_details.append(
                    {
                        "schedule_id": schedule.id,
                        "schedule_name": schedule.schedule_name,
                        "status": "started",
                    }
                )
                logger.info(f"이메일 스케줄 실행 시작: {schedule.id}")

            except Exception as e:
                failed_count += 1
                execution_details.append(
                    {
                        "schedule_id": schedule.id,
                        "schedule_name": schedule.schedule_name,
                        "status": "failed",
                        "error": str(e),
                    }
                )
                logger.error(f"이메일 스케줄 실행 실패: {schedule.id}, 오류: {str(e)}")

        return EmailScheduleExecuteResponse(
            message=f"이메일 스케줄 실행 완료: 성공 {executed_count}개, 실패 {failed_count}개",
            executed_count=executed_count,
            failed_count=failed_count,
            execution_time=current_time,
            details=execution_details,
        )

    except Exception as e:
        logger.error(f"이메일 스케줄 실행 중 오류: {str(e)}")
        raise ApiError(
            message=f"스케줄 실행 오류: {str(e)}",
            error_code=ErrorCodes.SCHEDULE_EXECUTE_FAILED,
            status_code=500,
        )


async def execute_single_email_schedule(schedule: Schedule, db: Session):
    """개별 이메일 스케줄 실행"""
    schedule_repo = ScheduleRepository(db)

    try:
        # 상태를 PROCESSING으로 변경
        schedule_repo.update_status(schedule.id, ScheduleStatus.PROCESSING)

        # 페이로드 파싱
        payload = json.loads(schedule.payload)

        # 이메일 서비스 초기화
        email_service = EmailService(db=db)

        # 대량 이메일인지 단일 이메일인지 확인
        if payload.get("is_bulk"):
            # 대량 이메일 발송
            bulk_request = BulkEmailRequest(
                recipients=[EmailRecipient(**r) for r in payload["recipients"]],
                subject=payload["subject"],
                html_body=payload["html_body"],
                sender_address=payload.get("sender_address"),
            )
            result = await email_service.send_bulk_email(
                bulk_request, api_key_id=schedule.api_key_id
            )
        else:
            # 단일 이메일 발송
            email_request = EmailRequest(
                to_email=payload["to_email"],
                to_name=payload.get("to_name"),
                subject=payload["subject"],
                html_body=payload["html_body"],
                sender_address=payload.get("sender_address"),
            )
            result = await email_service.send_single_email(
                email_request, api_key_id=schedule.api_key_id
            )

        # 성공 처리
        schedule_repo.update_status(
            schedule.id,
            ScheduleStatus.COMPLETED,
            executed_at=datetime.utcnow(),
            result=json.dumps(result),
        )

        logger.info(f"이메일 스케줄 실행 완료: {schedule.id}")

    except Exception as e:
        # 실패 처리
        schedule_repo.handle_failure(schedule.id, str(e))
        logger.error(f"이메일 스케줄 {schedule.id} 실행 실패: {str(e)}")
