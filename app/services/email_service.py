"""
이메일 서비스

이메일 발송 관련 비즈니스 로직
ncloud_mailer 모듈과 FastAPI를 연결하는 서비스 레이어
"""

import json
import logging
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

import requests
from sqlalchemy.orm import Session

from app.models.api_key import ApiKey
from app.models.email_log import EmailLog

# Repository import
from app.repositories.email_log_repository import EmailLogRepository

# FastAPI 스키마 import
from app.schemas.email import BulkEmailRequest, EmailRecipient, EmailRequest
from ncloud_mailer.config import NCloudConfig

# ncloud_mailer 모듈 import
from ncloud_mailer.ncloud_email import NCloudEmailSender

logger = logging.getLogger(__name__)


class EmailService:
    """이메일 서비스 클래스"""

    def __init__(self, db: Optional[Session] = None):
        """이메일 서비스 초기화"""
        try:
            self.config = NCloudConfig()
            self.sender = NCloudEmailSender(self.config)
            self.db = db
            if self.db:
                self.email_log_repo = EmailLogRepository(self.db)
            logger.info("이메일 서비스 초기화 완료")
        except Exception as e:
            logger.error(f"이메일 서비스 초기화 실패: {e}")
            raise

    def _get_sender_email_by_api_key(self, api_key_id: int) -> str:
        """
        API 키 ID로 해당 서비스의 발송자 이메일 주소를 가져옵니다.

        Args:
            api_key_id (int): API 키 ID

        Returns:
            str: 해당 서비스의 발송자 이메일 주소
        """
        if not self.db:
            # DB가 없으면 기본 발송자 사용
            return self.config.sender_address

        try:
            # API 키 정보 조회
            api_key = self.db.query(ApiKey).filter(ApiKey.id == api_key_id).first()

            if not api_key:
                logger.warning(
                    f"API 키 ID {api_key_id}를 찾을 수 없습니다. 기본 발송자 사용"
                )
                return self.config.sender_address

            # 서비스명에 따른 발송자 이메일 반환
            sender_email = self.config.get_sender_email_by_service(api_key.service_name)
            logger.info(
                f"API 키 ID {api_key_id} ({api_key.service_name}) -> 발송자: {sender_email}"
            )

            return sender_email

        except Exception as e:
            logger.error(f"API 키 기반 발송자 조회 실패: {e}. 기본 발송자 사용")
            return self.config.sender_address

    async def send_single_email(
        self, request: EmailRequest, api_key_id: int = 1
    ) -> Dict[str, Any]:
        """
        단일 이메일 발송

        Args:
            request: 이메일 발송 요청 데이터
            api_key_id: API 키 ID

        Returns:
            Dict: 발송 결과
        """
        # 고유 요청 ID 생성
        request_id = f"email_{uuid.uuid4().hex[:12]}"

        try:
            logger.info(f"단일 이메일 발송 시작: {request.to_email}")

            # API 키 기반 발송자 자동 선택 (요청에서 지정하지 않은 경우)
            sender_email = request.sender_address
            if not sender_email:
                sender_email = self._get_sender_email_by_api_key(api_key_id)
                logger.info(f"API 키 기반 발송자 자동 선택: {sender_email}")

            # 로그 저장 (발송 전)
            if self.db and hasattr(self, "email_log_repo"):
                await self._save_email_log(
                    api_key_id=api_key_id,
                    request_id=request_id,
                    sender_email=sender_email,
                    recipient_email=request.to_email,
                    recipient_name=request.to_name,
                    subject=request.subject,
                    body_html=request.html_body,
                    status="pending",
                )

            # NCloud API 호출
            result = self.sender.send_email(
                to_email=request.to_email,
                to_name=request.to_name,
                subject=request.subject,
                html_body=request.html_body,
                sender_address=sender_email,
            )

            # 로그 업데이트 (발송 성공)
            if self.db and hasattr(self, "email_log_repo"):
                await self._update_email_log(
                    request_id=request_id,
                    status="sent",
                    ncloud_request_id=result.get("requestId"),
                    ncloud_response=json.dumps(result),
                    sent_at=datetime.utcnow(),
                )

            logger.info(f"이메일 발송 성공: {result.get('requestId')}")

            return {
                "success": True,
                "message": "이메일이 성공적으로 발송되었습니다",
                "request_id": result.get("requestId"),
                "recipient_count": result.get("count", 1),
                "timestamp": datetime.now().isoformat(),
            }

        except ValueError as e:
            # 입력 검증 에러 (이메일 형식, 제목/내용 누락 등)
            logger.error(f"이메일 입력 검증 실패: {e}")
            if self.db and hasattr(self, "email_log_repo"):
                await self._update_email_log(
                    request_id=request_id, status="failed", error_message=str(e)
                )

            from app.exceptions import ErrorCodes, ApiError

            raise ApiError(
                message=f"이메일 입력 검증 실패: {str(e)}",
                error_code=ErrorCodes.EMAIL_INVALID_FORMAT,
                status_code=400,
            )

        except requests.RequestException as e:
            # NCloud API 요청 에러 (네트워크, 타임아웃, HTTP 에러 등)
            logger.error(f"NCloud API 요청 실패: {e}")
            if self.db and hasattr(self, "email_log_repo"):
                await self._update_email_log(
                    request_id=request_id, status="failed", error_message=str(e)
                )

            from app.exceptions import ErrorCodes, ApiError

            raise ApiError(
                message=f"이메일 발송 서비스 오류: {str(e)}",
                error_code=ErrorCodes.NCLOUD_API_ERROR,
                status_code=503,
            )

        except Exception as e:
            # 기타 예상치 못한 에러 (DB 에러, 시스템 에러 등)
            logger.error(f"이메일 발송 중 예상치 못한 오류: {e}")
            if self.db and hasattr(self, "email_log_repo"):
                await self._update_email_log(
                    request_id=request_id, status="failed", error_message=str(e)
                )

            from app.exceptions import ErrorCodes, ApiError

            raise ApiError(
                message=f"이메일 발송 중 시스템 오류가 발생했습니다: {str(e)}",
                error_code=ErrorCodes.EMAIL_SEND_FAILED,
                status_code=500,
            )

    async def send_bulk_email(
        self, request: BulkEmailRequest, api_key_id: int = 1
    ) -> Dict[str, Any]:
        """
        대량 이메일 발송

        Args:
            request: 대량 이메일 발송 요청 데이터
            api_key_id: API 키 ID (로그 저장용)

        Returns:
            Dict: 발송 결과
        """
        try:
            logger.info(f"대량 이메일 발송 시작: {len(request.recipients)}명")

            # API 키 기반 발송자 자동 선택 (요청에서 지정하지 않은 경우)
            sender_email = request.sender_address
            if not sender_email:
                sender_email = self._get_sender_email_by_api_key(api_key_id)
                logger.info(f"API 키 기반 발송자 자동 선택: {sender_email}")

            # 수신자 목록 변환
            recipients = [
                {"email": recipient.email, "name": recipient.name}
                for recipient in request.recipients
            ]

            # NCloud API 호출
            result = self.sender.send_bulk_email(
                recipients=recipients,
                subject=request.subject,
                html_body=request.html_body,
                sender_address=sender_email,
            )

            logger.info(f"대량 이메일 발송 성공: {result.get('requestId')}")

            return {
                "success": True,
                "message": f"{len(request.recipients)}명에게 이메일이 성공적으로 발송되었습니다",
                "request_id": result.get("requestId"),
                "recipient_count": result.get("count", len(request.recipients)),
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"대량 이메일 발송 실패: {e}")
            raise Exception(f"대량 이메일 발송 중 오류가 발생했습니다: {str(e)}")

    async def get_email_status(self, mail_id: str) -> Dict[str, Any]:
        """
        이메일 발송 상태 조회 (개별 메일)

        Args:
            mail_id: NCloud에서 반환한 메일 ID (mailId)

        Returns:
            Dict: 상태 조회 결과
        """
        try:
            logger.info(f"이메일 상태 조회: {mail_id}")

            # NCloud API 호출
            result = self.sender.get_email_status(mail_id)

            return {
                "mail_id": mail_id,
                "status": "조회 완료",
                "details": result,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"이메일 상태 조회 실패: {e}")
            raise Exception(f"이메일 상태 조회 중 오류가 발생했습니다: {str(e)}")

    async def get_mail_list(
        self, request_id: str, page: int = 0, size: int = 10
    ) -> Dict[str, Any]:
        """
        이메일 요청 목록 조회

        Args:
            request_id: 특정 요청 ID (필수)
            page: 페이지 번호
            size: 페이지 크기

        Returns:
            Dict: 메일 목록 조회 결과
        """
        try:
            if not request_id:
                raise ValueError("request_id는 필수입니다.")

            logger.info(
                f"메일 목록 조회: page={page}, size={size}, request_id={request_id}"
            )

            # NCloud API 호출
            result = self.sender.get_mail_list(request_id, page, size)

            return {
                "request_id": request_id,
                "page": page,
                "size": size,
                "status": "조회 완료",
                "details": result,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"메일 목록 조회 실패: {e}")
            raise Exception(f"메일 목록 조회 중 오류가 발생했습니다: {str(e)}")

    async def _save_email_log(self, **kwargs) -> None:
        """이메일 로그 저장"""
        try:
            email_log = EmailLog(**kwargs)
            self.db.add(email_log)
            self.db.commit()
            logger.info(f"이메일 로그 저장 완료: {kwargs.get('request_id')}")
        except Exception as e:
            self.db.rollback()
            logger.error(f"이메일 로그 저장 실패: {e}")

    async def _update_email_log(self, request_id: str, **kwargs) -> None:
        """이메일 로그 업데이트"""
        try:
            email_log = (
                self.db.query(EmailLog)
                .filter(EmailLog.request_id == request_id)
                .first()
            )
            if email_log:
                for key, value in kwargs.items():
                    if hasattr(email_log, key):
                        setattr(email_log, key, value)
                email_log.updated_at = datetime.utcnow()
                self.db.commit()
                logger.info(f"이메일 로그 업데이트 완료: {request_id}")
        except Exception as e:
            self.db.rollback()
            logger.error(f"이메일 로그 업데이트 실패: {e}")

    def health_check(self) -> Dict[str, Any]:
        """
        이메일 서비스 상태 확인

        Returns:
            Dict: 서비스 상태
        """
        try:
            # 설정 유효성 검사
            is_healthy = self.config.validate()

            return {
                "service": "email",
                "status": "healthy" if is_healthy else "unhealthy",
                "message": (
                    "이메일 서비스가 정상 동작 중입니다" if is_healthy else "설정 오류"
                ),
                "ncloud_config": is_healthy,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            return {
                "service": "email",
                "status": "error",
                "message": f"서비스 상태 확인 실패: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }
