"""
NCloud API 인증 모듈

NCloud Cloud Outbound Mailer API 인증을 위한 HMAC-SHA256 서명 생성을 담당합니다.
- HMAC-SHA256 서명 생성
- NCloud API 헤더 생성
"""

import time
import hmac
import hashlib
import base64
from typing import Dict


class NCloudAuth:
    """NCloud API 인증 클래스"""
    
    def __init__(self, access_key: str, secret_key: str):
        """
        NCloud 인증 정보 초기화
        
        Args:
            access_key (str): NCloud Access Key ID
            secret_key (str): NCloud Secret Key
        """
        self.access_key = access_key
        self.secret_key = secret_key
    
    def generate_signature(self, method: str, url: str, timestamp: str = None) -> str:
        """
        NCloud API 서명 생성
        
        Args:
            method (str): HTTP 메소드 (GET, POST, DELETE 등)
            url (str): 도메인을 제외한 URL 경로 (예: "/api/v1/mails")
            timestamp (str, optional): 타임스탬프. None이면 현재 시간 사용
        
        Returns:
            str: Base64로 인코딩된 HMAC-SHA256 서명
            
        Example:
            >>> auth = NCloudAuth("access_key", "secret_key")
            >>> signature = auth.generate_signature("POST", "/api/v1/mails")
        """
        if timestamp is None:
            timestamp = str(int(time.time() * 1000))  # 밀리초 단위
        
        # StringToSign 생성: METHOD + " " + URL + "\n" + TIMESTAMP + "\n" + ACCESS_KEY
        message = f"{method} {url}\n{timestamp}\n{self.access_key}"
        
        # HMAC-SHA256으로 서명 생성
        signature = hmac.new(
            key=self.secret_key.encode('utf-8'),
            msg=message.encode('utf-8'),
            digestmod=hashlib.sha256
        ).digest()
        
        # Base64로 인코딩
        return base64.b64encode(signature).decode('utf-8')
    
    def get_headers(self, method: str, url: str) -> Dict[str, str]:
        """
        NCloud API 호출에 필요한 헤더 생성
        
        Args:
            method (str): HTTP 메소드
            url (str): URL 경로
            
        Returns:
            Dict[str, str]: 인증 헤더 딕셔너리
        """
        timestamp = str(int(time.time() * 1000))
        signature = self.generate_signature(method, url, timestamp)
        
        return {
            'Content-Type': 'application/json',
            'x-ncp-apigw-timestamp': timestamp,
            'x-ncp-iam-access-key': self.access_key,
            'x-ncp-apigw-signature-v2': signature,
            'x-ncp-lang': 'ko-KR'
        }


# 테스트용 함수
def test_signature():
    """인증 서명 생성 테스트"""
    from .config import NCloudConfig
    
    print("=== NCloud 인증 서명 테스트 ===")
    
    # 설정 로드
    config = NCloudConfig()
    auth = NCloudAuth(config.access_key, config.secret_key)
    
    # 테스트 서명 생성
    signature = auth.generate_signature("POST", "/api/v1/mails", "1521787414578")
    print(f"✅ 서명 생성 성공: {signature[:8]}******")
    
    # 헤더 생성 테스트
    headers = auth.get_headers("POST", "/api/v1/mails")
    
    # print(f"생성된 헤더: {headers}")

    # 안전한 정보만 출력
    safe_headers = {
        'Content-Type': headers['Content-Type'],
        'x-ncp-apigw-timestamp': headers['x-ncp-apigw-timestamp'],
        'x-ncp-iam-access-key': f"{headers['x-ncp-iam-access-key'][:4]}*******",
        'x-ncp-apigw-signature-v2': f"{headers['x-ncp-apigw-signature-v2'][:8]}******",
        'x-ncp-lang': headers['x-ncp-lang']
    }
    print("✅ 헤더 생성 성공:")
    for key, value in safe_headers.items():
        print(f"   {key}: {value}")


if __name__ == "__main__":
    test_signature() 