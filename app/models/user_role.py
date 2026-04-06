# app/models/user_role.py
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, func, Table
from app.models.base import Base

# Option A — plain association table.
# We do not need to query who assigned a role in the current API contract.
# If assigned_at / assigned_by reporting is needed later, migrate to
# an association object pattern at that point.

user_roles = Table(
    "user_roles",
    Base.metadata,
    Column(
        "user_id",
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "role_id",
        Integer,
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)