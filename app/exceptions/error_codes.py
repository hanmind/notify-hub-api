"""
에러 코드 상수 정의

서비스에서 사용할 수 있는 모든 에러 코드
"""


class ErrorCodes:
    # =================================================================
    # 이메일 관련 에러 (10000번대)
    # =================================================================
    EMAIL_SEND_FAILED = "EMAIL_SEND_FAILED"  # 10001: 이메일 발송 실패
    EMAIL_INVALID_FORMAT = "EMAIL_INVALID_FORMAT"  # 10002: 이메일 형식 오류
    EMAIL_RECIPIENT_LIMIT_EXCEEDED = (
        "EMAIL_RECIPIENT_LIMIT_EXCEEDED"  # 10003: 수신자 수 한도 초과
    )
    EMAIL_TEMPLATE_NOT_FOUND = (
        "EMAIL_TEMPLATE_NOT_FOUND"  # 10004: 템플릿을 찾을 수 없음
    )
    EMAIL_CONTENT_TOO_LARGE = "EMAIL_CONTENT_TOO_LARGE"  # 10005: 이메일 내용이 너무 큼

    # =================================================================
    # 스케줄 관련 에러 (11000번대)
    # =================================================================
    SCHEDULE_NOT_FOUND = "SCHEDULE_NOT_FOUND"  # 11001: 스케줄을 찾을 수 없음
    SCHEDULE_ACCESS_DENIED = "SCHEDULE_ACCESS_DENIED"  # 11002: 스케줄 접근 권한 없음
    SCHEDULE_INVALID_TYPE = "SCHEDULE_INVALID_TYPE"  # 11003: 잘못된 스케줄 타입
    SCHEDULE_ALREADY_EXECUTED = "SCHEDULE_ALREADY_EXECUTED"  # 11004: 이미 실행된 스케줄
    SCHEDULE_ALREADY_CANCELLED = (
        "SCHEDULE_ALREADY_CANCELLED"  # 11005: 이미 취소된 스케줄
    )
    SCHEDULE_INVALID_TIME = "SCHEDULE_INVALID_TIME"  # 11006: 잘못된 예약 시간
    SCHEDULE_CREATE_FAILED = "SCHEDULE_CREATE_FAILED"  # 11007: 스케줄 생성 실패
    SCHEDULE_LIST_FAILED = "SCHEDULE_LIST_FAILED"  # 11008: 스케줄 목록 조회 실패
    SCHEDULE_EXECUTION_FAILED = "SCHEDULE_EXECUTION_FAILED"  # 11009: 스케줄 실행 실패
    SCHEDULE_CANCEL_FAILED = "SCHEDULE_CANCEL_FAILED"  # 11010: 스케줄 취소 실패
    SCHEDULE_EXECUTE_FAILED = (
        "SCHEDULE_EXECUTE_FAILED"  # 11011: 스케줄 실행 프로세스 실패
    )

    # =================================================================
    # 인증/권한 관련 에러 (20000번대)
    # =================================================================
    API_KEY_MISSING = "API_KEY_MISSING"  # 20001: API 키가 없음
    API_KEY_INVALID = "API_KEY_INVALID"  # 20002: 잘못된 API 키
    API_KEY_EXPIRED = "API_KEY_EXPIRED"  # 20003: 만료된 API 키
    API_KEY_INACTIVE = "API_KEY_INACTIVE"  # 20004: 비활성화된 API 키
    INSUFFICIENT_PERMISSION = "INSUFFICIENT_PERMISSION"  # 20005: 권한 부족

    # =================================================================
    # 데이터베이스 관련 에러 (30000번대)
    # =================================================================
    DATABASE_CONNECTION_ERROR = "DATABASE_CONNECTION_ERROR"  # 30001: DB 연결 실패
    RECORD_NOT_FOUND = "RECORD_NOT_FOUND"  # 30002: 레코드를 찾을 수 없음
    DUPLICATE_KEY_ERROR = "DUPLICATE_KEY_ERROR"  # 30003: 중복 키 에러
    DATABASE_TRANSACTION_ERROR = "DATABASE_TRANSACTION_ERROR"  # 30004: DB 트랜잭션 에러

    # =================================================================
    # 외부 서비스 관련 에러 (40000번대)
    # =================================================================
    NCLOUD_API_ERROR = "NCLOUD_API_ERROR"  # 40001: NCloud API 에러
    NCLOUD_AUTH_FAILED = "NCLOUD_AUTH_FAILED"  # 40002: NCloud 인증 실패
    NCLOUD_QUOTA_EXCEEDED = "NCLOUD_QUOTA_EXCEEDED"  # 40003: NCloud 할당량 초과
    EXTERNAL_API_TIMEOUT = "EXTERNAL_API_TIMEOUT"  # 40004: 외부 API 타임아웃
    EXTERNAL_API_UNAVAILABLE = "EXTERNAL_API_UNAVAILABLE"  # 40005: 외부 API 이용 불가

    # =================================================================
    # 일반적인 에러 (50000번대)
    # =================================================================
    VALIDATION_ERROR = "VALIDATION_ERROR"  # 50001: 유효성 검사 실패
    REQUEST_PARSING_ERROR = "REQUEST_PARSING_ERROR"  # 50002: 요청 파싱 에러
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"  # 50003: 내부 서버 에러
    UNKNOWN_ERROR = "UNKNOWN_ERROR"  # 50004: 알 수 없는 에러

    # =================================================================
    # SMS 관련 에러 (60000번대) - 향후 확장용
    # =================================================================
    SMS_SEND_FAILED = "SMS_SEND_FAILED"  # 60001: SMS 발송 실패
    SMS_INVALID_PHONE_NUMBER = "SMS_INVALID_PHONE_NUMBER"  # 60002: 잘못된 전화번호
