# 🔔 Notification Service API

통합 알림 서비스 API입니다. 사내 여러 서비스에서 공통으로 사용할 수 있는 이메일, SMS 발송 기능을 제공합니다.

> 📝 이 프로젝트는 인턴 기간 동안 맡았던 알림 서버 분리 프로젝트를 개인 포트폴리오용으로 정리한 것입니다. 따라서 실제 회사 정보는 모두 제거하였습니다.

## 📋 프로젝트 개요

- **목적**: 여러 서비스의 공통 알림 기능을 분리된 서버에서 통합 관리
- **기술 스택**: FastAPI, NCloud SENS, MySQL, AWS Lambda, SQLAlchemy
- **아키텍처 패턴**: Repository Pattern, Dependency Injection
- **주요 기능**: 이메일 발송, SMS 발송, 예약 발송, 발송 상태 조회

## 🛠️ 주요 기술 스택

### Backend
- **FastAPI**: 가볍고 빠른 Python 웹 프레임워크
- **SQLAlchemy**: ORM 및 데이터베이스 마이그레이션
- **Pydantic**: 데이터 검증 및 직렬화
- **Alembic**: 데이터베이스 마이그레이션 도구

### Infrastructure
- **NCloud SENS**: 이메일/SMS 발송 서비스
- **MySQL**: 관계형 데이터베이스
- **AWS Lambda**: 서버리스 스케줄링
- **Docker**: 컨테이너화

### Development
- **Repository Pattern**: 데이터 액세스 계층 분리
- **Dependency Injection**: 의존성 주입을 통한 테스트 용이성
- **API Documentation**: Swagger/OpenAPI 자동 생성

## 🏗️ 아키텍처 설계

```
📁 프로젝트 구조
├── 📁 app/
│   ├── 📁 models/           # SQLAlchemy 모델
│   ├── 📁 schemas/          # Pydantic 스키마
│   ├── 📁 repositories/     # Repository 패턴
│   ├── 📁 services/         # 비즈니스 로직
│   ├── 📁 routers/          # API 엔드포인트
│   ├── 📁 dependencies/     # 의존성 주입
│   └── 📁 exceptions/       # 예외 처리
├── 📁 ncloud_mailer/        # 독립 모듈
│   ├── ncloud_email.py      # 이메일 API
│   ├── ncloud_auth.py       # 인증 처리
│   └── config.py            # 설정 관리
└── 📁 scheduler/            # 스케줄링 시스템
    └── local_scheduler.py   # 로컬 스케줄러
```

## 📊 주요 구현 사항

### 1. Repository Pattern 구현
- **데이터 액세스 계층 분리**: 비즈니스 로직과 데이터베이스 액세스 분리
- **테스트 용이성**: Mock 객체를 통한 단위 테스트 가능
- **코드 재사용성**: 공통 CRUD 로직 추상화

### 2. 스케줄링 시스템
- **로컬 스케줄러**: 개발환경용 크론 스케줄러
- **AWS EventBridge**: 프로덕션 환경용 서버리스 스케줄링
- **재시도 메커니즘**: 실패한 작업에 대한 자동 재시도

### 3. API 설계
- **RESTful API**: 표준 HTTP 메소드 사용
- **API 키 인증**: X-API-Key 헤더 기반 인증
- **페이지네이션**: 대용량 데이터 처리
- **에러 핸들링**: 일관된 에러 응답 형식

## 🏗️ 프로젝트 구조

```
📁 프로젝트 구조
├── 📁 ncloud/                    # 독립 모듈
│   ├── ncloud_email.py          # 이메일 API
│   ├── ncloud_sms.py            # SMS API
│   └── test_ncloud.py           # 독립 테스트
├── 📁 services/                 # 비즈니스 로직
│   ├── email_service.py         # 종속성 있는 이메일 서비스
│   └── auth_service.py          # 인증 서비스
└── 📁 api/                      # FastAPI 엔드포인트
```

## 🚀 시작하기

### 1. 환경 설정

```bash
# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 패키지 설치
pip install -r requirements.txt
```

### 2. 환경변수 설정

#### 로컬 개발환경

`env.example` 파일을 참고하여 `.env` 파일을 생성하고 필요한 값들을 설정합니다:

```bash
# .env 파일 생성
cp env.example .env

# .env 파일 편집 (실제 값으로 변경)
ENVIRONMENT=local  # local이면 스케줄러 자동 활성화
SCHEDULER_INTERVAL_MINUTES=1

NCLOUD_ACCESS_KEY=your_ncloud_access_key
NCLOUD_SECRET_KEY=your_ncloud_secret_key
NCLOUD_SERVICE_ID=your_sens_service_id
```

#### 배포 환경 (AWS Lambda)

배포 환경에서는 다음과 같이 설정합니다:

```bash
ENVIRONMENT=production  # local이 아니면 스케줄러 자동 비활성화
```

### 📅 스케줄러 설정

#### 로컬 개발환경
- **로컬 스케줄러**: 자동 활성화 (1분마다 실행)
- **용도**: 개발/테스트용 예약 이메일 실행

#### 배포 환경
- **로컬 스케줄러**: 자동 비활성화
- **AWS EventBridge**: 예약 이메일 실행 담당
- **장점**: 서버리스 환경에 최적화

### 3. 개발 서버 실행

```bash
# 개발 서버 시작
python run.py

# 또는 uvicorn 직접 실행
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

서버가 시작되면 다음 주소에서 확인할 수 있습니다:
- **API 문서**: http://localhost:8000/docs (Swagger UI)
- **ReDoc**: http://localhost:8000/redoc
- **헬스 체크**: http://localhost:8000/health

## 📧 API 사용법

### 이메일 발송

```bash
# 단일 이메일 발송
curl -X POST "http://localhost:8000/api/v1/email/send" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: {YOUR_API_KEY}" \
  -d '{
    "to_email": "user@example.com",
    "to_name": "홍길동",
    "subject": "환영합니다!",
    "html_body": "<h1>가입을 축하합니다!</h1>",
    "sender_address": "noreply@example.com"
  }'

# 대량 이메일 발송
curl -X POST "http://localhost:8000/api/v1/email/send-bulk" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: {YOUR_API_KEY}" \
  -d '{
    "subject": "공지사항",
    "html_body": "<p>중요 공지입니다.</p>",
    "sender_address": "noreply@example.com",
    "recipients": [
      {"email": "user1@example.com", "name": "홍길동"},
      {"email": "user2@example.com", "name": "김철수"}
    ]
  }'
```

### 이메일 상태 조회

```bash
# 메일 상태 조회 (mail_id 기준)
curl -X GET "http://localhost:8000/api/v1/email/status/{mail_id}" \
  -H "X-API-Key: {YOUR_API_KEY}"

# 요청 ID로 발송 목록 조회 (mail_id 확인용)
curl -X GET "http://localhost:8000/api/v1/email/list/{request_id}" \
  -H "X-API-Key: {YOUR_API_KEY}"
```

### SMS 발송

```bash
# (임시) SMS 발송 엔드포인트 호출
curl -X POST "http://localhost:8000/api/v1/sms/send" \
  -H "X-API-Key: {YOUR_API_KEY}"
```

## 🔧 설정 정보

### 서비스 타입


### 이메일 템플릿 타입
- `1`: 회원가입
- `2`: 비번재설정
- `3`: 공지사항

### SMS 타입
- `SMS`: 단문 (90자 이하)
- `LMS`: 장문 (2000자 이하)
- `MMS`: 멀티미디어 (이미지 포함)

## 🗄️ 데이터베이스 설정

### MySQL 도커 실행

```bash
docker run -e MYSQL_ROOT_PASSWORD=password \
  -p 3306:3306 \
  -v ./data:/var/lib/mysql \
  -d mysql:8.0 \
  --character-set-server=utf8mb4 \
  --collation-server=utf8mb4_unicode_ci
```

## 🔍 테스트

```bash
pytest -q
```

## 📚 참고 자료

- [NCloud Cloud Outbound Mailer API](https://api.ncloud-docs.com/docs/ai-application-service-cloudoutboundmailer)
- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)

### 기술적 성과
- **Repository Pattern** 구현으로 코드 유지보수성 향상
- **의존성 주입** 패턴으로 테스트 용이성 증대
- **스케줄링 시스템** 구현으로 예약 발송 기능 제공
- **RESTful API** 설계로 확장성 확보
