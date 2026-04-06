from typing import List
from sqlalchemy import select

from app.models.role import Role
from app.repositories.base import BaseRepository

class RoleRepository(BaseRepository):

    async def get_by_ids(self, ids: List[int]) -> List[Role]:
        result = await self.db.execute(select(Role).where(Role.id.in_(ids)))
        return result.scalars().all()