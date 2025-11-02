from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.template import Template, TemplateType

from .base import BaseRepository


class TemplateRepository(BaseRepository[Template]):
    """템플릿 Repository"""

    def __init__(self, db: Session):
        super().__init__(Template, db)

    async def get_by_name(self, name: str) -> Optional[Template]:
        """템플릿 이름으로 조회"""
        return self.db.query(Template).filter(Template.template_name == name).first()

    async def get_by_type(self, template_type: TemplateType) -> List[Template]:
        """템플릿 타입으로 조회"""
        return (
            self.db.query(Template)
            .filter(Template.template_type == template_type)
            .all()
        )

    async def get_active_templates(self) -> List[Template]:
        """활성화된 템플릿 조회"""
        return self.db.query(Template).filter(Template.is_active == True).all()
