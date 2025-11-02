"""
FastAPI 개발 서버 실행 스크립트

개발 환경에서 FastAPI 앱을 실행하기 위한 편의 스크립트
Lambda 환경에서는 handler 함수를 엔트리 포인트로 사용
"""

import json
import logging
import os

import uvicorn
from mangum import Mangum

from app.main import app

mangum_handler = Mangum(app)

# 로거 초기화 (핸들러 외부에서)
logger = logging.getLogger()
logger.setLevel("INFO")


def handler(event, context):
    """
    AWS Lambda 핸들러 함수
    - event: Lambda 함수 이벤트 데이터를 포함하는 Dict
    - context: 함수 호출에 대한 정보를 포함하는 Lambda 런타임 컨텍스트

    Returns:
        Dict: HTTP 응답 (API Gateway 형식)
    """
    try:
        # 로깅: 함수 시작
        logger.info(f"Lambda 함수 시작: {context.function_name}")
        logger.info(f"요청 ID: {context.aws_request_id}")

        # Mangum을 통해 FastAPI 앱 실행
        response = mangum_handler(event, context)

        # 로깅: 성공적인 응답
        logger.info(f"Lambda 함수 완료: {response.get('statusCode', 'Unknown')}")

        return response

    except Exception as e:
        # 예외 처리 및 로깅
        logger.error(f"Lambda 함수 실행 중 오류 발생: {str(e)}")
        logger.error(f"이벤트 데이터: {event}")

        # 에러 응답 반환
        return {
            "statusCode": 503,
            "message": "Lambda 함수 실행 중 오류가 발생했습니다.",
            # "body": json.dumps(
            #     {
            #         "error": "Internal Server Error",
            #         "message": "Lambda 함수 실행 중 오류가 발생했습니다.",
            #     }
            # ),
            # "headers": {"Content-Type": "application/json"},
        }


if __name__ == "__main__":
    # 로컬 개발 환경에서만 실행
    uvicorn.run(
        "app.main:app",  # 앱 위치
        host="127.0.0.1",  # 로컬호스트 (클릭 가능한 주소)
        port=8000,  # 포트 번호
        reload=True,  # 코드 변경시 자동 재시작
        log_level="info",  # 로그 레벨
    )
