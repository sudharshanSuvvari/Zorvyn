# app/models/user.py
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, generate_uuid


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id           : Mapped[str]            = mapped_column(String(36), primary_key=True, default=generate_uuid)
    email        : Mapped[str]            = mapped_column(String(255), unique=True,  nullable=False, index=True)
    password_hash: Mapped[str]            = mapped_column(String(255), nullable=False)
    full_name    : Mapped[str]            = mapped_column(String(255), nullable=False)
    is_active    : Mapped[bool]           = mapped_column(Boolean,     default=True,  nullable=False)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # ── relationships ─────────────────────────────────────────────────────────
    roles: Mapped[List["Role"]] = relationship(
        "Role",
        secondary="user_roles",
        back_populates="users",
        lazy="selectin",        # always loaded — required by permission guard
    )

    financial_records: Mapped[List["FinancialRecord"]] = relationship(
        "FinancialRecord",
        back_populates="creator",
        lazy="noload",          # never auto-loaded — fetched only when explicitly needed
    )

    audit_logs: Mapped[List["AuditLog"]] = relationship(
        "AuditLog",
        foreign_keys="AuditLog.actor_id",
        back_populates="actor",
        lazy="noload",
    )

    def __repr__(self) -> str:
        return f"<User {self.email}>"