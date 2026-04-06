# app/services/dashboard_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case
from datetime import date, datetime
from decimal import Decimal

from app.models.financial_record import FinancialRecord
from app.models.category import Category
from app.schemas.dashboard import (
    SummaryResponse, CategoryTotalItem, TrendPoint, RecentActivityItem,
)
from app.utils.csv_export import build_csv_response
from app.utils.date_utils import resolve_date_range

class DashboardService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_summary(self, date_from: date | None, date_to: date | None) -> SummaryResponse:
        date_from, date_to = resolve_date_range(date_from, date_to)

        result = await self.db.execute(
            select(
                func.sum(case((FinancialRecord.type == "income",  FinancialRecord.amount), else_=0)).label("income"),
                func.sum(case((FinancialRecord.type == "expense", FinancialRecord.amount), else_=0)).label("expenses"),
                func.count(FinancialRecord.id).label("count"),
            ).where(
                FinancialRecord.status == "posted",
                FinancialRecord.record_date >= date_from,
                FinancialRecord.record_date <= date_to,
            )
        )
        row = result.one()
        income   = row.income   or Decimal("0")
        expenses = row.expenses or Decimal("0")

        return SummaryResponse(
            total_income=income,
            total_expenses=expenses,
            net_balance=income - expenses,
            currency="USD",
            record_count=row.count,
            period={"from": str(date_from), "to": str(date_to)},
        )

    async def get_by_category(self, date_from: date | None, date_to: date | None, type_filter: str | None) -> list[CategoryTotalItem]:
        date_from, date_to = resolve_date_range(date_from, date_to)

        q = (
            select(
                Category.id.label("category_id"),
                Category.name.label("category_name"),
                func.sum(FinancialRecord.amount).label("total"),
                func.count(FinancialRecord.id).label("count"),
            )
            .join(Category, FinancialRecord.category_id == Category.id)
            .where(
                FinancialRecord.status == "posted",
                FinancialRecord.record_date >= date_from,
                FinancialRecord.record_date <= date_to,
            )
            .group_by(Category.id, Category.name)
            .order_by(func.sum(FinancialRecord.amount).desc())
        )
        if type_filter:
            q = q.where(FinancialRecord.type == type_filter)

        rows = (await self.db.execute(q)).all()
        grand_total = sum(r.total for r in rows) or Decimal("1")  # avoid div by zero

        return [
            CategoryTotalItem(
                category_id=r.category_id,
                category_name=r.category_name,
                total=r.total,
                percentage=round(float(r.total / grand_total) * 100, 2),
                count=r.count,
            )
            for r in rows
        ]

    async def get_trends(self, granularity: str, date_from: date | None, date_to: date | None) -> list[TrendPoint]:
        date_from, date_to = resolve_date_range(date_from, date_to)

        # period label: "2025-01" for monthly, "2025-W04" for weekly
        if granularity == "monthly":
            period_expr = func.to_char(FinancialRecord.record_date, "YYYY-MM")
        else:
            period_expr = func.to_char(FinancialRecord.record_date, "IYYY-\"W\"IW")

        rows = (await self.db.execute(
            select(
                period_expr.label("period"),
                func.sum(case((FinancialRecord.type == "income",  FinancialRecord.amount), else_=0)).label("income"),
                func.sum(case((FinancialRecord.type == "expense", FinancialRecord.amount), else_=0)).label("expenses"),
            )
            .where(
                FinancialRecord.status == "posted",
                FinancialRecord.record_date >= date_from,
                FinancialRecord.record_date <= date_to,
            )
            .group_by("period")
            .order_by("period")
        )).all()

        return [
            TrendPoint(period=r.period, income=r.income or Decimal("0"),
                       expenses=r.expenses or Decimal("0"),
                       net=(r.income or Decimal("0")) - (r.expenses or Decimal("0")))
            for r in rows
        ]

    async def get_recent_activity(self, limit: int) -> list[RecentActivityItem]:
        rows = (await self.db.execute(
            select(FinancialRecord, Category.name.label("category_name"))
            .join(Category, FinancialRecord.category_id == Category.id)
            .where(FinancialRecord.status == "posted")
            .order_by(FinancialRecord.record_date.desc(), FinancialRecord.created_at.desc())
            .limit(limit)
        )).all()

        return [
            RecentActivityItem(
                id=str(r.FinancialRecord.id),
                type=r.FinancialRecord.type,
                amount=r.FinancialRecord.amount,
                currency=r.FinancialRecord.currency,
                category_name=r.category_name,
                record_date=r.FinancialRecord.record_date,
                description=r.FinancialRecord.description,
            )
            for r in rows
        ]

    async def export_csv(self, date_from: date | None, date_to: date | None, type_filter: str | None):
        date_from, date_to = resolve_date_range(date_from, date_to)
        q = (
            select(FinancialRecord, Category.name.label("category_name"))
            .join(Category, FinancialRecord.category_id == Category.id)
            .where(
                FinancialRecord.record_date >= date_from,
                FinancialRecord.record_date <= date_to,
            )
            .order_by(FinancialRecord.record_date.desc())
        )
        if type_filter:
            q = q.where(FinancialRecord.type == type_filter)

        rows = (await self.db.execute(q)).all()
        return build_csv_response(rows)