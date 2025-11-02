"""
NCloud 이메일 발송 모듈

NCloud Cloud Outbound Mailer API를 통한 이메일 발송 기능을 제공합니다.
"""

import json
import os
import requests
from typing import List, Dict, Any, Optional
from .ncloud_auth import NCloudAuth
from .config import NCloudConfig


class NCloudEmailSender:
    """NCloud 이메일 발송 클래스"""
    
    def __init__(self, config: Optional[NCloudConfig] = None):
        """
        NCloud 이메일 발송기 초기화
        
        Args:
            config (NCloudConfig, optional): 설정 객체. None이면 기본 설정 사용
        """
        self.config = config if config else NCloudConfig()
        self.auth = NCloudAuth(self.config.access_key, self.config.secret_key)
        self.base_url = self.config.API_BASE_URL
        
    def send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        to_name: Optional[str] = None,
        sender_address: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        단일 이메일 발송
        
        Args:
            to_email (str): 수신자 이메일
            subject (str): 이메일 제목
            html_body (str): HTML 이메일 내용
            to_name (str, optional): 수신자 이름
            sender_address (str, optional): 발신자 이메일 (기본값: config에서 가져옴)
            
        Returns:
            Dict[str, Any]: NCloud API 응답
            
        Raises:
            requests.RequestException: HTTP 요청 실패
            ValueError: 잘못된 매개변수
            
        Example:
            >>> sender = NCloudEmailSender()
            >>> result = sender.send_email(
            ...     to_email="user@example.com",
            ...     subject="환영합니다!",
            ...     html_body="<h1>가입을 축하합니다!</h1>"
            ... )
        """
        # 입력 검증
        if not to_email or '@' not in to_email:
            raise ValueError(f"유효하지 않은 이메일 주소: {to_email}")
        
        if not subject.strip():
            raise ValueError("이메일 제목은 비어있을 수 없습니다.")
            
        if not html_body.strip():
            raise ValueError("이메일 내용은 비어있을 수 없습니다.")
        
        # NCloud API 요청 데이터 구성
        request_data = {
            "senderAddress": sender_address or self.config.sender_address,
            "title": subject,
            "body": html_body,
            "recipients": [
                {
                    "address": to_email,
                    "name": to_name or "",
                    "type": "R"  # R: 수신자, C: 참조, B: 숨은참조
                }
            ],
            "individual": True,    # 개별 발송 (각 수신자별로 개별 이메일)
            "advertising": False   # 광고성 이메일 여부
        }
        
        return self._send_request("/api/v1/mails", request_data)
    
    def send_bulk_email(
        self,
        recipients: List[Dict[str, str]],
        subject: str,
        html_body: str,
        sender_address: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        대량 이메일 발송
        
        Args:
            recipients (List[Dict]): 수신자 목록
                [{"email": "user1@example.com", "name": "홍길동"}, ...]
            subject (str): 이메일 제목
            html_body (str): HTML 이메일 내용
            sender_address (str, optional): 발신자 이메일
            
        Returns:
            Dict[str, Any]: NCloud API 응답
            
        Example:
            >>> recipients = [
            ...     {"email": "user1@example.com", "name": "홍길동"},
            ...     {"email": "user2@example.com", "name": "김철수"}
            ... ]
            >>> result = sender.send_bulk_email(recipients, "공지사항", "<h1>중요 공지</h1>")
        """
        if not recipients:
            raise ValueError("수신자 목록이 비어있습니다.")
        
        # 수신자 목록 변환
        ncloud_recipients = []
        for recipient in recipients:
            if 'email' not in recipient:
                raise ValueError("수신자 정보에 'email' 필드가 필요합니다.")
            
            ncloud_recipients.append({
                "address": recipient['email'],
                "name": recipient.get('name', ''),
                "type": "R"
            })
        
        request_data = {
            "senderAddress": sender_address or self.config.sender_address,
            "title": subject,
            "body": html_body,
            "recipients": ncloud_recipients,
            "individual": True,
            "advertising": False
        }
        
        return self._send_request("/api/v1/mails", request_data)
    
    def get_email_status(self, mail_id: str) -> Dict[str, Any]:
        """
        이메일 발송 상태 조회 (개별 메일)
        
        Args:
            mail_id (str): NCloud에서 반환한 메일 ID (mailId)
            
        Returns:
            Dict[str, Any]: 이메일 상태 정보
        """
        if not mail_id:
            raise ValueError("mail_id는 필수입니다.")
            
        return self._send_request(f"/api/v1/mails/{mail_id}", method="GET")
    
    def get_mail_list(self, request_id: str, page: int = 0, size: int = 10) -> Dict[str, Any]:
        """
        이메일 요청 목록 조회
        
        Args:
            request_id (str): 특정 요청 ID (필수)
            page (int): 페이지 번호 (기본값: 0)
            size (int): 페이지 크기 (기본값: 10)
            
        Returns:
            Dict[str, Any]: 메일 목록 정보
        """
        if not request_id:
            raise ValueError("request_id는 필수입니다.")
            
        params = f"?page={page}&size={size}"
        endpoint = f"/api/v1/mails/requests/{request_id}/mails{params}"
        
        return self._send_request(endpoint, method="GET")
    
    def _send_request(
        self, 
        endpoint: str, 
        data: Optional[Dict[str, Any]] = None, 
        method: str = "POST"
    ) -> Dict[str, Any]:
        """
        NCloud API에 HTTP 요청 전송
        
        Args:
            endpoint (str): API 엔드포인트 (예: "/api/v1/mails")
            data (Dict, optional): 요청 데이터 (POST인 경우)
            method (str): HTTP 메소드 (GET, POST, DELETE)
            
        Returns:
            Dict[str, Any]: API 응답 데이터
            
        Raises:
            requests.RequestException: HTTP 요청 실패
            ValueError: API 에러 응답
        """
        # 드라이런 모드: 외부 API 호출 없이 성공 응답 시뮬레이션
        if os.getenv("NCLOUD_DRY_RUN", "false").lower() in ("1", "true", "yes"): 
            if method.upper() == "POST":
                # 대량 발송 여부에 따라 count 계산
                count = 1
                if isinstance(data, dict) and isinstance(data.get("recipients"), list):
                    count = max(1, len(data.get("recipients")))
                return {
                    "requestId": f"dryrun-{abs(hash(endpoint)) % 10_000_000}",
                    "count": count,
                    "dryRun": True,
                }
            # GET 류 요청의 경우 간단한 조회 결과 반환
            return {
                "requestId": f"dryrun-{abs(hash(endpoint)) % 10_000_000}",
                "status": "S",
                "items": [],
                "dryRun": True,
            }

        url = self.base_url + endpoint
        headers = self.auth.get_headers(method, endpoint)
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, timeout=30)
            elif method.upper() == "POST":
                response = requests.post(
                    url, 
                    headers=headers, 
                    data=json.dumps(data, ensure_ascii=False).encode('utf-8'),
                    timeout=30
                )
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers, timeout=30)
            else:
                raise ValueError(f"지원하지 않는 HTTP 메소드: {method}")
            
            # HTTP 상태 코드 확인
            if response.status_code not in [200, 201]:
                error_msg = f"API 요청 실패 (HTTP {response.status_code})"
                try:
                    error_detail = response.json()
                    error_msg += f": {error_detail}"
                except:
                    error_msg += f": {response.text}"
                
                raise requests.RequestException(error_msg)
            
            # JSON 응답 파싱
            return response.json()
            
        except requests.Timeout:
            raise requests.RequestException("API 요청 시간 초과 (30초)")
        except requests.ConnectionError:
            raise requests.RequestException("NCloud API 서버에 연결할 수 없습니다.")
        except json.JSONDecodeError:
            raise requests.RequestException(f"유효하지 않은 JSON 응답: {response.text}")

# # 편의 함수
# def create_email_sender(config: Optional[NCloudConfig] = None) -> NCloudEmailSender:
#     """이메일 발송기 생성 (편의 함수)"""
#     return NCloudEmailSender(config)

# 테스트용 함수
def test_email_sender():
    """이메일 발송기 기본 테스트"""
    print("=== NCloud 이메일 발송기 테스트 ===")
    
    try:
        # 설정 로드
        from .config import NCloudConfig
        config = NCloudConfig()
        
        # 이메일 발송기 생성
        sender = NCloudEmailSender(config)
        print("✅ 이메일 발송기 생성 성공")
        
        # 테스트 데이터 (실제 발송은 하지 않음)
        test_data = {
            # "to_email": "test@example.com",
            "to_email": "user@example.com",
            "to_name": "테스트 사용자",
            "subject": "테스트 이메일",
            "html_body": "<h1>테스트입니다!</h1><p>NCloud 이메일 발송 테스트</p>"
        }
        
        print(f"✅ 테스트 데이터 준비 완료")
        print(f"   - 수신자: {test_data['to_email']}")
        print(f"   - 제목: {test_data['subject']}")
        print(f"   - 발신자: {config.sender_address}")
        
        # # 실제 API 호출은 주석 처리 (비용 발생 방지)
        # result = sender.send_email(**test_data)
        # print(f"✅ 이메일 발송 성공: {result}")
        
        print("📝 실제 발송은 주석 처리됨 (비용 절약)")
        
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")


if __name__ == "__main__":
    test_email_sender() 