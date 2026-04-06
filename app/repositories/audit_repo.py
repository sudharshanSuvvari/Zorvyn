# app/repositories/audit_repo.py

from app.models.audit_log import AuditLog
from app.repositories.base import BaseRepository


class AuditRepository(BaseRepository):

    async def log(self, data: dict):
        audit = AuditLog(**data)
        self.db.add(audit)
        await self.db.flush()
        return audit