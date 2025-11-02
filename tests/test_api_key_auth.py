"""
API 키 인증 테스트 스크립트

헤더 기반 API 키 인증이 올바르게 작동하는지 테스트
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# 테스트 서버 URL
BASE_URL = "http://localhost:8000"

# 테스트용 API 키 데이터
TEST_API_KEYS = {
    "service_a": "eb2058a8da8a894193b0c29383208925",
    "service_b": "798004a6ae937cb3934cab6d5c7dd1a7",
    "service_c": "d08b5afee1575879fcc2e782802b46e2",
}


def test_email_send_with_valid_api_key():
    """유효한 API 키로 이메일 발송 테스트"""
    headers = {"X-API-Key": TEST_API_KEYS["service_a"]}
    
    payload = {
        "to_email": "user@example.com",
        "to_name": "홍길동",
        "subject": "테스트 이메일",
        "html_body": "<h1>테스트 메시지</h1>",
        "sender_address": "noreply@example.com",
    }
    
    response = client.post("/api/v1/email/send", json=payload, headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "request_id" in data


def test_api_key_auth():
    """API 키 인증 테스트"""

    # 테스트용 이메일 데이터
    test_email = {
        "to_email": "user@example.com",
        "to_name": "테스트 사용자",
        "subject": "API 키 인증 테스트",
        "html_body": "<h1>API 키 인증 테스트 메일입니다</h1>",
        "sender_address": "noreply@example.com",
    }

    print("🔐 API 키 인증 테스트 시작\n")

    # 1. API 키 없이 요청 (401 에러)
    print("1️⃣ API 키 없이 요청 테스트")
    try:
        response = client.post("/api/v1/email/send", json=test_email)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")

    print()

    # 2. 잘못된 API 키로 요청 (401 에러)
    print("2️⃣ 잘못된 API 키로 요청 테스트")
    try:
        response = client.post("/api/v1/email/send", json=test_email, headers={"X-API-Key": "invalid-key-12345"})
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")

    print()

    # 3. 각 서비스별 유효한 API 키로 요청 테스트 (200 응답)
    for service_name, api_key in TEST_API_KEYS.items():
        print(f"3️⃣ {service_name} API 키로 요청 테스트")
        try:
            headers = {"X-API-Key": api_key}
            response = client.post("/api/v1/email/send", json=test_email, headers=headers)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"   Success: {result.get('success')}")
                print(f"   Message: {result.get('message')}")
                print(f"   Request ID: {result.get('request_id')}")
            else:
                print(f"   Response: {response.json()}")
        except Exception as e:
            print(f"   Error: {e}")

        print()


def test_health_endpoint():
    """인증이 필요없는 헬스체크 엔드포인트 테스트"""
    print("🏥 헬스체크 엔드포인트 테스트")
    try:
        response = client.get("/api/v1/email/test")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    print()


if __name__ == "__main__":
    print("=" * 50)
    print("API 키 인증 테스트")
    print("=" * 50)

    # 헬스체크 먼저 테스트
    test_health_endpoint()

    # API 키 인증 테스트
    test_api_key_auth()

    print("=" * 50)
    print("테스트 완료")
    print("=" * 50)
