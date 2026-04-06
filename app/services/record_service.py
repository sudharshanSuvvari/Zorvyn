# app/services/record_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal

from app.core.audit import write_audit
from app.core.exceptions import NotFoundError, ConflictError, ForbiddenOperationError
from app.models.category import Category
from app.repositories.record_repo import RecordRepository
from app.repositories.category_repo import CategoryRepository
from app.schemas.record import RecordCreate, RecordUpdate, RecordFilterParams
from app.schemas.common import PaginatedResponse
from app.models.financial_record import FinancialRecord

class RecordService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = RecordRepository(FinancialRecord, db)
        self.cat_repo = CategoryRepository(Category, db)

    async def list_records(self, filters: RecordFilterParams) -> PaginatedResponse:
        items, total = await self.repo.list_filtered(filters)
        return PaginatedResponse(items=items, total=total,
                                 page=filters.page, page_size=filters.page_size)

    async def get_record(self, record_id: str) -> FinancialRecord:
        record = await self.repo.get_with_relations(record_id)
        if not record:
            raise NotFoundError(f"Record {record_id} not found")
        return record

    async def create_record(self, payload: RecordCreate, actor_id: str) -> FinancialRecord:
        category = await self.cat_repo.get_by_id(payload.category_id)
        if not category:
            raise NotFoundError(f"Category {payload.category_id} not found")

        # enforce category type must match record type
        if category.type != payload.type:
            raise ConflictError(
                f"Category '{category.name}' is of type '{category.type}' "
                f"but record type is '{payload.type}'"
            )

        record = FinancialRecord(
            type=payload.type,
            amount=payload.amount,
            currency=payload.currency,
            category_id=payload.category_id,
            record_date=payload.record_date,
            description=payload.description,
            status=payload.status,
            created_by=actor_id,
        )
        created = await self.repo.create(record)
        await self.db.commit()

        await write_audit(self.db, actor_id=actor_id, entity_type="financial_record",
                          entity_id=created.id, action="created",
                          after=payload.model_dump(mode="json"))
        return created

    async def update_record(self, record_id: str, payload: RecordUpdate, actor_id: str) -> FinancialRecord:
        record = await self.repo.get_with_relations(record_id)
        if not record:
            raise NotFoundError(f"Record {record_id} not found")
        if record.status == "void":
            raise ConflictError("A voided record is immutable and cannot be updated")

        before = {"amount": str(record.amount), "status": record.status,
                  "category_id": record.category_id, "description": record.description}

        if payload.category_id is not None:
            category = await self.cat_repo.get_by_id(payload.category_id)
            if not category:
                raise NotFoundError(f"Category {payload.category_id} not found")
            if category.type != record.type:
                raise ConflictError(f"Category type '{category.type}' does not match record type '{record.type}'")
            record.category_id = payload.category_id

        if payload.amount is not None:
            record.amount = payload.amount
        if payload.description is not None:
            record.description = payload.description
        if payload.record_date is not None:
            record.record_date = payload.record_date
        if payload.status is not None:
            record.status = payload.status

        await self.db.commit()
        await write_audit(self.db, actor_id=actor_id, entity_type="financial_record",
                          entity_id=record_id, action="updated",
                          before=before, after=payload.model_dump(exclude_none=True, mode="json"))
        return record

    async def delete_record(self, record_id: str, actor_id: str) -> None:
        record = await self.repo.get_with_relations(record_id)
        if not record:
            raise NotFoundError(f"Record {record_id} not found")

        record.status = "void"
        await self.db.commit()
        await write_audit(self.db, actor_id=actor_id, entity_type="financial_record",
                          entity_id=record_id, action="voided")

    async def get_record_history(self, record_id: str):
        record = await self.repo.get_by_id(record_id)
        if not record:
            raise NotFoundError(f"Record {record_id} not found")
        return await self.repo.get_audit_trail(record_id)