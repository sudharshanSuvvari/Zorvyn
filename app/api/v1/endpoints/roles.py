# app/api/v1/endpoints/roles.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.db_connection import get_db
from app.api.dependencies import require_permission
from app.schemas.role import RoleResponse
from app.schemas.permission import AssignPermissionRequest
from app.services.role_service import RoleService
from app.models.user import User

role_router = APIRouter()

@role_router.get("", response_model=list[RoleResponse])
async def list_roles(
    current_user: User = Depends(require_permission("roles", "list")),
    db: AsyncSession = Depends(get_db),
):
    return await RoleService(db).list_roles()

@role_router.post("/{role_id}/permissions", status_code=204)
async def assign_permission(
    role_id: int,
    payload: AssignPermissionRequest,
    current_user: User = Depends(require_permission("roles", "manage")),
    db: AsyncSession = Depends(get_db),
):
    await RoleService(db).assign_permission(role_id, payload.permission_id)

@role_router.delete("/{role_id}/permissions/{permission_id}", status_code=204)
async def revoke_permission(
    role_id: int,
    permission_id: int,
    current_user: User = Depends(require_permission("roles", "manage")),
    db: AsyncSession = Depends(get_db),
):
    await RoleService(db).revoke_permission(role_id, permission_id)