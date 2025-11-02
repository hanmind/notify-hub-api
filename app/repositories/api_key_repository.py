from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.api_key import ApiKey

from .base import BaseRepository


class ApiKeyRepository(BaseRepository[ApiKey]):
    """API 키 Repository"""

    def __init__(self, db: Session):
        super().__init__(ApiKey, db)

    async def get_by_api_key(self, api_key: str) -> Optional[ApiKey]:
        """API 키로 조회"""
        return self.db.query(ApiKey).filter(ApiKey.api_key == api_key).first()

    async def get_by_service(self, service_name: str) -> List[ApiKey]:
        """서비스명으로 조회"""
        return self.db.query(ApiKey).filter(ApiKey.service_name == service_name).all()

    async def get_active_keys(self) -> List[ApiKey]:
        """활성화된 API 키 조회"""
        return self.db.query(ApiKey).filter(ApiKey.is_active == True).all()
