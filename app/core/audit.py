# app/core/audit.py  — write audit log after every mutating action
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.audit_log import AuditLog
import uuid, datetime

async def write_audit(
    db: AsyncSession,
    actor_id: str,
    entity_type: str,
    entity_id: str,
    action: str,
    before: dict | None = None,
    after: dict | None = None,
    ip_address: str | None = None,
):
    log = AuditLog(
        id=str(uuid.uuid4()),
        actor_id=actor_id,
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        before_state=before,
        after_state=after,
        ip_address=ip_address,
        occurred_at=datetime.datetime.utcnow(),
    )
    db.add(log)
    await db.commit()