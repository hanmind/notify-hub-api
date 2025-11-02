"""
API 예외 클래스 정의

비즈니스 로직에서 발생하는 사용자 정의 예외들을 정의합니다.
"""

class ApiError(Exception):
    """
    API 커스텀 예외 클래스
    
    비즈니스 로직 실행 중 발생하는 예외 상황을 처리하기 위한 커스텀 예외입니다.
    HTTP 상태 코드와 에러 코드를 포함하여 클라이언트에게 구체적인 에러 정보를 제공합니다.
    
    Attributes:
        message (str): 에러 메시지
        error_code (str): 에러 코드 (예: USER_NOT_FOUND)
        status_code (int): HTTP 상태 코드 (기본값: 400)
        
    Example:
        >>> raise ApiError("사용자를 찾을 수 없습니다", "USER_NOT_FOUND", 404)
    """
    
    def __init__(self, message: str, error_code: str, status_code: int = 400):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        super().__init__(self.message)
    
    def __str__(self):
        return self.message
    
    def __repr__(self):
        return f"ApiError(message='{self.message}', error_code='{self.error_code}', status_code={self.status_code})"
