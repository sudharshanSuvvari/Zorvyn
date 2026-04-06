# app/models/audit_log.py
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional, TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import JSON

from app.models.base import Base, generate_uuid

if TYPE_CHECKING:
    from app.models.user import User


class AuditLog(Base):
    # AuditLog deliberately excludes TimestampMixin —
    # it has a single occurred_at field and must never be updated.
    __tablename__ = "audit_logs"

    id          : Mapped[str]            = mapped_column(String(36), primary_key=True, default=generate_uuid)
    actor_id    : Mapped[Optional[str]]  = mapped_column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True,  index=True)
    entity_type : Mapped[str]            = mapped_column(String(50), nullable=False, index=True)
    entity_id   : Mapped[str]            = mapped_column(String(36), nullable=False, index=True)
    action      : Mapped[str]            = mapped_column(String(50), nullable=False)
    before_state: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    after_state : Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    ip_address  : Mapped[Optional[str]]  = mapped_column(String(45), nullable=True)   # 45 covers IPv6
    occurred_at : Mapped[datetime]       = mapped_column(DateTime,   server_default=func.now(), nullable=False, index=True)

    # ── relationships ─────────────────────────────────────────────────────────
    actor: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[actor_id],
        back_populates="audit_logs",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<AuditLog {self.action} on {self.entity_type}:{self.entity_id} by {self.actor_id}>"