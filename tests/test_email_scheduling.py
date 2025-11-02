"""
이메일 스케줄링 테스트 스크립트

발송 수단별 스케줄링 구조 테스트
"""

import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# 테스트용 API 키 데이터
TEST_API_KEYS = {
    "service_a": "eb2058a8da8a894193b0c29383208925",
    "service_b": "798004a6ae937cb3934cab6d5c7dd1a7",
    "service_c": "d08b5afee1575879fcc2e782802b46e2",
}


def test_create_email_schedule():
    """이메일 스케줄 생성 테스트"""
    headers = {"X-API-Key": TEST_API_KEYS["service_a"]}
    
    payload = {
        "schedule_name": "테스트 스케줄",
        "scheduled_at": (datetime.now() + timedelta(hours=1)).isoformat(),
        "to_email": "user@example.com",
        "to_name": "홍길동",
        "subject": "예약 테스트 이메일",
        "html_body": "<h1>예약 발송 테스트</h1>",
        "max_retry": 3,
        "retry_interval": 300,
    }
    
    response = client.post("/api/v1/email/schedule", json=payload, headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "schedule_id" in data


def test_email_schedule_list():
    """이메일 스케줄 목록 조회 테스트"""
    print("\n2. 📋 이메일 스케줄 목록 조회 테스트")

    try:
        response = client.get("/api/v1/email/schedule/list", headers={"X-API-Key": TEST_API_KEYS["service_a"]})

        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   Total Count: {result.get('total_count')}")
            print(f"   Schedules: {len(result.get('schedules', []))}")

            for schedule in result.get("schedules", [])[:3]:  # 최대 3개만 출력
                print(
                    f"     - ID: {schedule.get('schedule_id')}, Name: {schedule.get('schedule_name')}"
                )
                print(
                    f"       Status: {schedule.get('status')}, Scheduled: {schedule.get('scheduled_at')}"
                )
        else:
            print(f"   Error: {response.json()}")

    except Exception as e:
        print(f"   Exception: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("이메일 스케줄링 테스트 시작")
    print("=" * 60)

    # 1. 단일 이메일 스케줄 생성
    test_create_email_schedule()

    # 2. 스케줄 목록 조회
    test_email_schedule_list()

    print("\n" + "=" * 60)
    print("이메일 스케줄링 테스트 완료")
    print("=" * 60)
