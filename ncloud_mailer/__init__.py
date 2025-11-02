"""
NCloud SENS(Simple & Easy Notification Service) API 클라이언트

이메일, SMS 발송을 위한 NCloud SENS API 연동 모듈입니다.
주요 기능:
- 이메일 발송 (단일/대량)
- SMS 발송 (단일/대량)
- 발송 상태 조회
- 템플릿 기반 발송

Usage:
    from ncloud_mailer import NCloudAuth, NCloudEmail
    
    auth = NCloudAuth(access_key, secret_key)
    email = NCloudEmail(auth, service_id)
"""

__version__ = "1.0.0"

# 주요 클래스들을 import할 수 있도록 준비
# from .ncloud_auth import NCloudAuth
# from .ncloud_email import NCloudEmail
# from .ncloud_template import NCloudTemplate 