# app/services/role_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.core.exceptions import NotFoundError, ConflictError, ForbiddenOperationError
from app.models.permission import Permission
from app.models.role import Role
from app.repositories.role_repo import RoleRepository
from app.repositories.permission_repo import PermissionRepository

class RoleService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = RoleRepository(Role, db)
        self.perm_repo = PermissionRepository(Permission, db)

    async def list_roles(self):
        return await self.repo.list_with_permissions()

    async def assign_permission(self, role_id: int, permission_id: int) -> None:
        role = await self.repo.get_with_permissions(role_id)
        if not role:
            raise NotFoundError(f"Role {role_id} not found")

        perm = await self.perm_repo.get_by_id(permission_id)
        if not perm:
            raise NotFoundError(f"Permission {permission_id} not found")

        already_assigned = any(p.id == permission_id for p in role.permissions)
        if already_assigned:
            raise ConflictError("Permission already assigned to this role")

        role.permissions.append(perm)
        await self.db.commit()

    async def revoke_permission(self, role_id: int, permission_id: int) -> None:
        role = await self.repo.get_with_permissions(role_id)
        if not role:
            raise NotFoundError(f"Role {role_id} not found")

        # admin role must always retain at least one permission
        if role.name == "admin" and len(role.permissions) <= 1:
            raise ForbiddenOperationError("Cannot remove the last permission from the admin role")

        role.permissions = [p for p in role.permissions if p.id != permission_id]
        await self.db.commit()