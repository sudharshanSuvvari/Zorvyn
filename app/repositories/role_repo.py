from typing import List
from sqlalchemy import select

from app.models.role import Role
from app.repositories.base import BaseRepository

class RoleRepository(BaseRepository):

    async def get_by_ids(self, ids: List[int]) -> List[Role]:
        result = await self.db.execute(select(Role).where(Role.id.in_(ids)))
        return result.scalars().all()
    
    async def list_with_permissions(self) -> List[Role]:
        result = await self.db.execute(
            select(Role)
        )
        return result.scalars().all()
    
    async def get_with_permissions(self, role_id: int) -> Role | None:
        result = await self.db.execute(
            select(Role).where(Role.id == role_id)
        )
        return result.scalar_one_or_none()