from typing import List
from sqlalchemy import select
from app.models.permission import Permission
from app.repositories.base import BaseRepository

class PermissionRepository(BaseRepository):

    async def get_by_ids(self, ids: List[int]) -> List[Permission]:
        result = await self.db.execute(select(Permission).where(Permission.id.in_(ids)))
        return result.scalars().all()