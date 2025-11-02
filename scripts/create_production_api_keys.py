#!/usr/bin/env python3
"""
프로덕션 API 키 생성 스크립트

데이터베이스에 서비스별 API 키를 생성합니다.
"""

import asyncio
import os
import sys
from datetime import datetime

# 프로젝트 루트 디렉토리를 sys.path에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.base import Base
from app.models.api_key import ApiKey
from app.repositories.api_key_repository import ApiKeyRepository

import hashlib

from app.models.api_key import ApiKey
from app.models.base import SessionLocal


def generate_api_key(service_name, environment="PROD"):
    """hashlib을 사용하여 API 키 생성"""
    key_string = f"{service_name.upper()}_{environment}"
    api_key = hashlib.md5(key_string.encode("utf-8")).hexdigest()
    return api_key


def create_service_api_keys():
    """실제 서비스들의 API 키 생성"""
    db = SessionLocal()

    # 서비스 정보 정의
    services = [
        {
            "key_name": "서비스 A",
            "service_name": "service_a",
            "hash_key": "SERVICE_A",
            "description": "서비스 A에서 사용하는 알림 서비스 API 키",
        },
        {
            "key_name": "서비스 B",
            "service_name": "service_b",
            "hash_key": "SERVICE_B",
            "description": "서비스 B에서 사용하는 알림 서비스 API 키",
        },
        {
            "key_name": "서비스 C",
            "service_name": "service_c",
            "hash_key": "SERVICE_C",
            "description": "서비스 C에서 사용하는 알림 서비스 API 키",
        },
    ]

    created_keys = []

    try:
        print("🔑 실제 서비스용 API 키 생성 시작")
        print("=" * 50)

        for service in services:
            # 기존 키 확인
            existing_key = (
                db.query(ApiKey)
                .filter(ApiKey.service_name == service["service_name"])
                .first()
            )

            if existing_key:
                print(
                    f"✅ {service['service_name']}: 기존 키 사용 (ID: {existing_key.id})"
                )
                created_keys.append(existing_key)
                continue

            # API 키 생성
            api_key = generate_api_key(service["hash_key"], "PROD")

            # 데이터베이스에 저장
            new_api_key = ApiKey(
                key_name=service["key_name"],
                api_key=api_key,
                service_name=service["service_name"],
                is_active=True,
                description=service["description"],
            )

            db.add(new_api_key)
            db.commit()
            db.refresh(new_api_key)

            print(f"🎉 {service['service_name']}: 새 키 생성")
            print(f"   - ID: {new_api_key.id}")
            print(f"   - Hash Key: {service['hash_key']}_PROD")
            print(f"   - API Key: {api_key}")
            print(f"   - 활성화: {new_api_key.is_active}")
            print()

            created_keys.append(new_api_key)

        print("✅ 모든 서비스 API 키 생성 완료!")
        print(f"📊 총 {len(created_keys)}개의 API 키가 준비되었습니다.")

        return created_keys

    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        db.rollback()
        return []
    finally:
        db.close()


def show_api_key_summary():
    """생성된 API 키 요약 정보 출력"""
    db = SessionLocal()

    try:
        all_keys = db.query(ApiKey).all()

        print("\n📋 현재 등록된 API 키 목록")
        print("=" * 50)

        for key in all_keys:
            status = "🟢 활성" if key.is_active else "🔴 비활성"
            print(f"ID: {key.id} | {key.service_name} | {status}")
            print(f"   키: {key.api_key}")
            print(f"   설명: {key.description}")
            print()

    except Exception as e:
        print(f"❌ API 키 조회 오류: {e}")
    finally:
        db.close()


def test_hash_generation():
    """해시 생성 테스트"""
    print("🧪 해시 생성 테스트")
    print("=" * 40)

    services = ["SERVICE_A_PROD", "SERVICE_B_PROD", "SERVICE_C_PROD"]
    for service in services:
        hash_value = hashlib.md5(service.encode("utf-8")).hexdigest()
        print(f"{service} → {hash_value}")


if __name__ == "__main__":
    print("🚀 통합 알림 서비스 API 키 생성")
    print("=" * 60)

    # 1. 해시 생성 테스트
    test_hash_generation()
    print()

    # 2. 실제 API 키 생성
    created_keys = create_service_api_keys()

    # 3. 요약 정보 출력
    show_api_key_summary()

    if created_keys:
        print("API 키 생성 끝")
    else:
        print("❌ API 키 생성에 실패했습니다.")
