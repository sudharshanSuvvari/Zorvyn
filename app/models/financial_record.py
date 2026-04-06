# app/models/financial_record.py
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Optional, TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint, Date, DateTime, ForeignKey,
    Integer, Numeric, String, Text, func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, generate_uuid

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.category import Category


class FinancialRecord(Base, TimestampMixin):
    __tablename__ = "financial_records"
    __table_args__ = (
        CheckConstraint("type IN ('income', 'expense')",                    name="ck_record_type"),
        CheckConstraint("status IN ('draft', 'posted', 'void')",            name="ck_record_status"),
        CheckConstraint("amount > 0",                                       name="ck_record_amount_positive"),
        CheckConstraint("currency IN ('USD','EUR','GBP','INR','JPY','AUD','CAD')", name="ck_record_currency"),
    )

    id         : Mapped[str]             = mapped_column(String(36),   primary_key=True, default=generate_uuid)
    created_by : Mapped[str]             = mapped_column(String(36),   ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    category_id: Mapped[int]             = mapped_column(Integer,      ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False, index=True)
    amount     : Mapped[Decimal]         = mapped_column(Numeric(12, 2), nullable=False)
    type       : Mapped[str]             = mapped_column(String(10),   nullable=False)
    currency   : Mapped[str]             = mapped_column(String(3),    nullable=False, default="USD")
    record_date: Mapped[date]            = mapped_column(Date,         nullable=False, index=True)
    description: Mapped[Optional[str]]   = mapped_column(Text,         nullable=True)
    status     : Mapped[str]             = mapped_column(String(10),   nullable=False, default="posted")

    # ── relationships ─────────────────────────────────────────────────────────
    creator: Mapped["User"] = relationship(
        "User",
        foreign_keys=[created_by],
        back_populates="financial_records",
        lazy="selectin",
    )

    category: Mapped["Category"] = relationship(
        "Category",
        back_populates="financial_records",
        lazy="selectin",        # always loaded — every record response includes category
    )

    def __repr__(self) -> str:
        return f"<FinancialRecord {self.type} {self.amount} {self.currency} on {self.record_date}>"