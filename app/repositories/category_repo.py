# app/repositories/category_repo.py

from sqlalchemy import select
from app.models import Category, FinancialRecord
from app.repositories.base import BaseRepository


class CategoryRepository(BaseRepository):

    # async def get_by_id(self, category_id: int) -> Category | None:
    #     result = await self.db.execute(
    #         select(Category).where(Category.id == category_id)
    #     )
    #     return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Category | None:
        result = await self.db.execute(
            select(Category).where(Category.name == name)
        )
        return result.scalar_one_or_none()
    
    async def is_in_use(self, category_id: int) -> bool:
        selected = await self.db.execute(
            select(FinancialRecord).where(FinancialRecord.category_id == category_id)
        )
        return selected.scalar_one_or_none() is not None
    
    async def list_all(self, type_filter: str | None = None) -> list[Category]:
        query = select(Category)
        if type_filter:
            query = query.where(Category.type == type_filter)
        result = await self.db.execute(query)
        return result.scalars().all()