import os
from datetime import datetime

from dotenv import load_dotenv
from sqlalchemy import Column, DateTime, Integer, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


# 환경 감지 및 적절한 .env 파일 로드
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
    print(f"🌍 Environment: {server_env} (using {env_file})")


# 환경변수 로드
load_environment()

Base = declarative_base()

# Database configuration - 환경변수 사용
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_NAME = os.getenv("DB_NAME", "notification_service")

print(f"🔧 DB 환경변수 로딩:")
print(f"   - DB_HOST: {DB_HOST}")
print(f"   - DB_PORT: {DB_PORT}")
print(f"   - DB_USER: {DB_USER}")
print(f"   - DB_NAME: {DB_NAME}")

# DATABASE_URL 환경변수가 있으면 우선 사용, 없으면 개별 변수로 구성
DATABASE_URL = (
    os.getenv("DATABASE_URL")
    or f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

print(f"🔗 Database URL: mysql+pymysql://{DB_USER}:***@{DB_HOST}:{DB_PORT}/{DB_NAME}")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class TimestampMixin:
    """공통 타임스탬프 필드를 제공하는 Mixin 클래스"""

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


def get_db():
    """데이터베이스 세션을 제공하는 의존성 함수"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
