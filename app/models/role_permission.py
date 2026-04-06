# app/models/role_permission.py
from sqlalchemy import Column, Integer, ForeignKey, Table
from app.models.base import Base

# Plain association table — no extra columns needed on this join
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column(
        "role_id",
        Integer,
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "permission_id",
        Integer,
        ForeignKey("permissions.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)