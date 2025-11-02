"""
로컬 크론 스케줄러 테스트

로컬 스케줄러가 정상 작동하는지 확인하는 테스트
"""

import asyncio
import os
from datetime import datetime, timedelta

import httpx
import pytest
from app.scheduler.local_scheduler import LocalScheduler

BASE_URL = "http://localhost:8000"


async def test_scheduler_status():
    """스케줄러 상태 확인"""
    print("1️⃣ 스케줄러 상태 확인")

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/v1/scheduler/status")

        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 스케줄러 실행 중: {data['scheduler']['running']}")
            print(f"   📊 활성화: {data['scheduler']['enabled']}")
            print(f"   ⏰ 실행 간격: {data['scheduler']['interval_minutes']}분")
            print(f"   💬 상태: {data['scheduler']['message']}")
            return True
        else:
            print(f"   ❌ 서버 연결 실패: {response.status_code}")
            return False


async def test_create_schedule():
    """테스트 스케줄 생성"""
    print("\n2️⃣ 테스트 스케줄 생성")

    # UTC 시간 사용
    scheduled_time = datetime.utcnow() + timedelta(minutes=1)

    schedule_data = {
        "schedule_name": "로컬 스케줄러 자동 테스트",
        "scheduled_at": scheduled_time.isoformat() + "Z",
        "timezone": "UTC",  # UTC로 명시적 설정
        "to_email": "user@example.com",
        "to_name": "홍길동",
        "subject": "🤖 로컬 스케줄러 테스트",
        "html_body": f"<h1>로컬 스케줄러 테스트</h1><p>이 메일은 {scheduled_time.strftime('%Y-%m-%d %H:%M:%S')} UTC에 로컬 스케줄러에 의해 자동 발송되었습니다.</p>",
        "sender_address": "noreply@example.com",
        "max_retry": 3,
        "retry_interval": 300,
    }

    async with httpx.AsyncClient() as client:
        headers = {"X-API-Key": "test-key-12345"}
        response = await client.post(
            f"{BASE_URL}/api/v1/email/schedule/create",
            json=schedule_data,
            headers=headers,
        )

        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 스케줄 생성 완료: ID {data['schedule_id']}")
            print(
                f"   📅 예약 시간: {scheduled_time.strftime('%Y-%m-%d %H:%M:%S')} UTC"
            )
            print(
                f"   🇰🇷 한국 시간: {(scheduled_time + timedelta(hours=9)).strftime('%Y-%m-%d %H:%M:%S')} KST"
            )
            print("   ⏱️ 1분 후 자동 실행됩니다!")
            return data["schedule_id"]
        else:
            print(f"   ❌ 스케줄 생성 실패: {response.status_code}")
            print(f"   오류 내용: {response.text}")
            return None


async def test_pending_schedules():
    """대기 중인 스케줄 확인"""
    print("\n3️⃣ 대기 중인 스케줄 확인")

    async with httpx.AsyncClient() as client:
        headers = {"X-API-Key": "test-key-12345"}

        response = await client.get(
            f"{BASE_URL}/api/v1/email/schedule/list?status=pending", headers=headers
        )

        if response.status_code == 200:
            data = response.json()
            print(f"   📋 총 개수: {data['total_count']}")

            for schedule in data["schedules"][:5]:  # 최대 5개만 표시
                print(f"   - ID {schedule['schedule_id']}: {schedule['schedule_name']}")
                print(f"     예약 시간: {schedule['scheduled_at']}")
        else:
            print(f"   ❌ 목록 조회 실패: {response.status_code}")


async def main():
    """메인 테스트 실행"""
    print("🧪 로컬 스케줄러 테스트 시작")
    print("=" * 50)

    try:
        # 1. 스케줄러 상태 확인
        if not await test_scheduler_status():
            return

        # 2. 테스트 스케줄 생성
        schedule_id = await test_create_schedule()

        # 3. 대기 중인 스케줄 확인
        await test_pending_schedules()

        # 4. 결과 안내
        print("\n" + "=" * 50)
        print("✅ 테스트 완료!")
        print("📊 실시간 로그는 FastAPI 서버 콘솔에서 확인하세요.")
        print("\n💡 시간대 정보:")
        print(f"   - 현재 UTC 시간: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
        print(
            f"   - 현재 한국 시간: {(datetime.utcnow() + timedelta(hours=9)).strftime('%Y-%m-%d %H:%M:%S')}"
        )

        if schedule_id:
            print(f"\n🚀 스케줄 ID {schedule_id}이 1분 후 자동 실행됩니다!")

    except Exception as e:
        print(f"❌ 테스트 실행 중 오류: {str(e)}")


if __name__ == "__main__":
    # 메인 테스트 실행
    asyncio.run(main())


class TestLocalScheduler:
    """로컬 스케줄러 테스트 클래스"""
    
    def setup_method(self):
        """테스트 전 설정"""
        self.scheduler = LocalScheduler()
    
    def test_schedule_creation(self):
        """스케줄 생성 테스트"""
        schedule_data = {
            "schedule_name": "테스트 스케줄",
            "scheduled_at": datetime.now() + timedelta(minutes=1),
            "to_email": "user@example.com",
            "to_name": "홍길동",
            "subject": "테스트 이메일",
            "html_body": "<h1>테스트 메시지</h1>",
            "sender_address": "noreply@example.com",
        }
        
        result = self.scheduler.create_schedule(schedule_data)
        
        assert result is not None
        assert result["schedule_name"] == "테스트 스케줄"
