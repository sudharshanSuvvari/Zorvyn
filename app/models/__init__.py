# app/models/__init__.py
# Import order matters here — tables must be defined before any
# relationship that references them by string name is resolved.
# Association tables first, then entities, then dependent entities.

from app.models.base import Base, TimestampMixin, generate_uuid  # noqa: F401

from app.models.role_permission import role_permissions           # noqa: F401
from app.models.user_role import user_roles                       # noqa: F401

from app.models.permission import Permission                      # noqa: F401
from app.models.role import Role                                  # noqa: F401
from app.models.user import User                                  # noqa: F401
from app.models.category import Category                          # noqa: F401
from app.models.financial_record import FinancialRecord           # noqa: F401
from app.models.audit_log import AuditLog                         # noqa: F401