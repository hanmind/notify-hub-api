from typing import Generic, List, Optional, Type, TypeVar

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """기본 Repository 클래스 - 공통 CRUD 작업을 제공"""

    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db

    async def create(self, obj_in: dict) -> ModelType:
        """새 객체 생성"""
        try:
            db_obj = self.model(**obj_in)
            self.db.add(db_obj)
            self.db.commit()
            self.db.refresh(db_obj)
            return db_obj
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e

    async def get(self, id: int) -> Optional[ModelType]:
        """ID로 객체 조회"""
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_by_id(self, id: int) -> Optional[ModelType]:
        """ID로 객체 조회 (동기 버전)"""
        return self.db.query(self.model).filter(self.model.id == id).first()

    async def get_multi(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """여러 객체 조회 (페이징)"""
        return self.db.query(self.model).offset(skip).limit(limit).all()

    async def update(self, db_obj: ModelType, obj_in: dict) -> ModelType:
        """객체 업데이트"""
        try:
            for field, value in obj_in.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)

            self.db.commit()
            self.db.refresh(db_obj)
            return db_obj
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e

    async def delete(self, id: int) -> bool:
        """객체 삭제"""
        try:
            db_obj = await self.get(id)
            if db_obj:
                self.db.delete(db_obj)
                self.db.commit()
                return True
            return False
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e

    async def count(self) -> int:
        """전체 객체 수 조회"""
        return self.db.query(self.model).count()
