"""
NCloud 모듈 설정 관리

환경변수를 읽어와서 NCloud API 연동에 필요한 설정값을 제공합니다.
"""

import os
from typing import Optional

from dotenv import load_dotenv


def load_environment():
    """환경에 따라 적절한 .env 파일을 로드"""
    # server 환경변수로 환경 구분
    server_env = os.getenv("server", "local")

    if server_env == "dev":
        # 개발/Lambda 환경: .env.dev 사용
        env_file = ".env.dev"
    else:
        # 로컬 환경: .env 사용
        env_file = ".env"

    load_dotenv(env_file)
    print(f"🌍 NCloud Environment: {server_env} (using {env_file})")


class NCloudConfig:
    """NCloud 설정 클래스"""

    # NCloud Cloud Outbound Mailer API 엔드포인트
    API_BASE_URL = "https://mail.apigw.ntruss.com"

    def __init__(self, env_file: Optional[str] = None):
        """
        설정 초기화

        Args:
            env_file (str, optional): .env 파일 경로
        """
        if env_file:
            load_dotenv(env_file)
        else:
            # 환경 감지 로직 사용
            load_environment()

    @property
    def access_key(self) -> str:
        """NCloud Access Key ID"""
        key = os.getenv("NCLOUD_ACCESS_KEY")
        if not key:
            raise ValueError("NCLOUD_ACCESS_KEY 환경변수가 설정되지 않았습니다.")
        return key

    @property
    def secret_key(self) -> str:
        """NCloud Secret Key"""
        key = os.getenv("NCLOUD_SECRET_KEY")
        if not key:
            raise ValueError("NCLOUD_SECRET_KEY 환경변수가 설정되지 않았습니다.")
        return key

    @property
    def sender_address(self) -> str:
        """기본 발신자 이메일 주소 (NCloud에서 인증된 이메일)"""
        sender = os.getenv("NCLOUD_SENDER_EMAIL")
        if not sender:
            raise ValueError(
                "NCLOUD_SENDER_EMAIL 환경변수가 설정되지 않았습니다. NCloud에서 인증된 발신자 이메일을 설정하세요."
            )
        return sender

    def get_sender_email_by_service(self, service_name: str) -> str:
        """
        서비스명에 따른 발송자 이메일 주소 반환

        Args:
            service_name (str): 서비스명 (service_a, service_b, service_c)
            
        Returns:
            str: 대응하는 발송자 이메일 주소
        """
        # 서비스명 → 발송자 이메일 매핑
        service_email_map = {
            "service_a": "SERVICE_A",
            "service_b": "SERVICE_B", 
            "service_c": "SERVICE_C",
        }

        # 서비스명 정규화
        service_key = service_email_map.get(service_name, service_name.upper())

        # 환경변수 키 생성
        env_key = f"NCLOUD_SENDER_EMAIL_{service_key}"

        # 서비스별 발송자 이메일 조회
        sender_email = os.getenv(env_key)

        if sender_email:
            return sender_email

        # 서비스별 설정이 없으면 기본값 사용
        return self.sender_address

    def load_env_file(self, env_file: str) -> None:
        """
        .env 파일을 읽어서 환경변수로 설정

        Args:
            env_file (str): .env 파일 경로
        """
        try:
            with open(env_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        os.environ[key.strip()] = value.strip()
        except FileNotFoundError:
            print(f"Warning: {env_file} 파일을 찾을 수 없습니다.")

    def validate(self) -> bool:
        """
        필수 설정값들이 모두 있는지 검증

        Returns:
            bool: 모든 필수 설정이 있으면 True
        """
        try:
            self.access_key
            self.secret_key
            return True
        except ValueError:
            return False

    def __str__(self) -> str:
        """설정 정보 출력 (보안 정보는 마스킹)"""
        try:
            access_key_display = f"{self.access_key[:4]}*******"
            secret_key_display = "***설정됨***"
        except ValueError:
            access_key_display = "***설정되지 않음***"
            secret_key_display = "***설정되지 않음***"

        return f"""
NCloud Config:
- API Base URL: {self.API_BASE_URL}
- Access Key: {access_key_display}
- Secret Key: {secret_key_display}
- Sender Email: {self.sender_address}
        """.strip()


# 테스트용 함수
def test_config():
    """설정 테스트"""
    print("=== NCloud 설정 테스트 ===")

    # 설정 객체 생성
    config = NCloudConfig()

    print(f"설정 유효성: {config.validate()}")
    print(config)


if __name__ == "__main__":
    test_config()
