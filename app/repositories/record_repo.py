# app/repositories/record_repo.py

from sqlalchemy import select
from app.models.financial_record import FinancialRecord
from app.repositories.base import BaseRepository


class RecordRepository(BaseRepository):

    async def create(self, data: dict) -> FinancialRecord:
        record = FinancialRecord(**data)
        self.db.add(record)
        await self.db.flush()
        return record


    # async def get_by_id(self, record_id: str) -> FinancialRecord | None:
    #     result = await self.db.execute(
    #         select(FinancialRecord).where(FinancialRecord.id == record_id)
    #     )
    #     return result.scalar_one_or_none()


    async def list(self, filters: dict):
        query = select(FinancialRecord)

        if "user_id" in filters:
            query = query.where(FinancialRecord.created_by == filters["user_id"])

        if "type" in filters:
            query = query.where(FinancialRecord.type == filters["type"])

        if "category_id" in filters:
            query = query.where(FinancialRecord.category_id == filters["category_id"])

        if "from_date" in filters:
            query = query.where(FinancialRecord.record_date >= filters["from_date"])

        if "to_date" in filters:
            query = query.where(FinancialRecord.record_date <= filters["to_date"])

        result = await self.db.execute(query)
        return result.scalars().all()