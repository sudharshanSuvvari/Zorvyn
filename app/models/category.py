# app/models/category.py
from __future__ import annotations

from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import Boolean, Integer, String, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.financial_record import FinancialRecord


class Category(Base, TimestampMixin):
    __tablename__ = "categories"
    __table_args__ = (
        CheckConstraint("type IN ('income', 'expense')", name="ck_category_type"),
    )

    id       : Mapped[int]           = mapped_column(Integer, primary_key=True, autoincrement=True)
    name     : Mapped[str]           = mapped_column(String(100), unique=True, nullable=False)
    type     : Mapped[str]           = mapped_column(String(20),  nullable=False)
    color_hex: Mapped[Optional[str]] = mapped_column(String(7),   nullable=True)
    is_system: Mapped[bool]          = mapped_column(Boolean, default=False, nullable=False)

    # ── relationships ─────────────────────────────────────────────────────────
    financial_records: Mapped[List["FinancialRecord"]] = relationship(
        "FinancialRecord",
        back_populates="category",
        lazy="noload",
    )

    def __repr__(self) -> str:
        return f"<Category {self.name} ({self.type})>"