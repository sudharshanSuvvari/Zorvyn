# app/repositories/user_repo.py

from sqlalchemy import select, func, update
from sqlalchemy.orm import selectinload

from app.models import User
from app.models import user_roles
from app.models import Role
from app.models import role_permission

from app.repositories.base import BaseRepository

class UserRepository(BaseRepository):

    # async def get_by_id(self, user_id: str) -> User | None:
    #     result = await self.db.execute(
    #         select(User).where(User.id == user_id)
    #     )
    #     return result.scalar_one_or_none()


    async def get_with_roles(self, user_id: str) -> User | None:
        """
        Loads:
        User → user_roles → Role → role_permission → Permission
        """

        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
   
    async def get_by_email(self, email: str) -> User | None:
        """
        Loads: User details for hash_verification
        """

        result = await self.db.execute(
            select(User)
            .where(User.email == email)
        )

        return result.scalar_one_or_none()
    
    async def update_last_login(self, user_id: str):
        await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(last_login_at=func.now())
        )
        await self.db.commit()


    async def list_paginated(
        self,
        page: int,
        page_size: int,
        is_active: bool | None = None,
        role_name: str | None = None,
    ) -> tuple[list[User], int]:
        """
        Returns a tuple of (items, total_count).
        The service layer wraps this into PaginatedResponse.
        Repository never touches schemas — it only returns ORM objects.
        """
        offset = (page - 1) * page_size

        # ── base query ────────────────────────────────────────────────────────────
        query = select(User)

        # ── filters ───────────────────────────────────────────────────────────────
        if is_active is not None:
            query = query.where(User.is_active == is_active)

        if role_name is not None:
            query = query.join(User.roles).where(Role.name == role_name)  # .roles not .role

        # ── count — runs against filtered base query before pagination ────────────
        count_query = select(func.count()).select_from(query.subquery())
        total: int = await self.db.scalar(count_query)

        # ── data — paginated and ordered ──────────────────────────────────────────
        data_query = (
            query
            .order_by(User.created_at.desc())   # created_at is more meaningful than id.desc()
            .offset(offset)
            .limit(page_size)
        )

        result = await self.db.execute(data_query)
        users = result.scalars().all()

        return users, total