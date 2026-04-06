# app/services/user_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.core.security import hash_password
from app.core.audit import write_audit
from app.core.exceptions import NotFoundError, ConflictError, ForbiddenOperationError
from app.repositories.user_repo import UserRepository
from app.repositories.role_repo import RoleRepository
from app.schemas.user import UserCreate, UserListResponse, UserUpdate
from app.schemas.common import PaginatedResponse
from app.models.user import User
from app.models.role import Role

class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = UserRepository(User, db)
        self.role_repo = RoleRepository(Role, db)

    async def list_users(
        self,
        page: int,
        page_size: int,
        is_active: bool | None,
        role_name: str | None,
    ) -> PaginatedResponse[UserListResponse]:

        users, total = await self.repo.list_paginated(
            page=page,
            page_size=page_size,
            is_active=is_active,
            role_name=role_name,
        )

        return PaginatedResponse[UserListResponse](
            items=[UserListResponse.model_validate(u) for u in users],
            total=total,
            page=page,
            page_size=page_size,
        )

    async def get_user(self, user_id: str) -> User:
        user = await self.repo.get_with_roles(user_id)
        if not user:
            raise NotFoundError(f"User {user_id} not found")
        return user

    async def create_user(self, payload: UserCreate, actor_id: str) -> User:
        existing = await self.repo.get_by_email(payload.email)
        if existing:
            raise ConflictError("A user with this email already exists")

        roles = await self.role_repo.get_by_ids(payload.role_ids)
        if len(roles) != len(payload.role_ids):
            raise NotFoundError("One or more role IDs are invalid")

        user = User(
            email=payload.email,
            password_hash=hash_password(payload.password),
            full_name=payload.full_name,
            is_active=True,
            roles=roles,
        )
        created = await self.repo.create(user)
        await self.db.commit()

        await write_audit(self.db, actor_id=actor_id, entity_type="user",
                          entity_id=created.id, action="created",
                          after={"email": created.email, "roles": payload.role_ids})
        return created

    async def update_user(self, user_id: str, payload: UserUpdate, actor_id: str) -> User:
        user = await self.repo.get_with_roles(user_id)
        if not user:
            raise NotFoundError(f"User {user_id} not found")

        before = {"full_name": user.full_name, "is_active": user.is_active}

        if payload.full_name is not None:
            user.full_name = payload.full_name
        if payload.is_active is not None:
            # await self._guard_last_admin(user_id, payload.is_active)
            user.is_active = payload.is_active
        if payload.role_ids is not None:
            roles = await self.role_repo.get_by_ids(payload.role_ids)
            if len(roles) != len(payload.role_ids):
                raise NotFoundError("One or more role IDs are invalid")
            user.roles = roles

        await self.db.commit()
        await write_audit(self.db, actor_id=actor_id, entity_type="user",
                          entity_id=user_id, action="updated",
                          before=before, after=payload.model_dump(exclude_none=True))
        return user

    async def delete_user(self, user_id: str, actor_id: str) -> None:
        print(f"Attempting to delete user {user_id} by actor {actor_id}")
        if user_id == actor_id:
            raise ForbiddenOperationError("You cannot deactivate your own account")
        user = await self.repo.get_with_roles(user_id)
        if not user:
            raise NotFoundError(f"User {user_id} not found")

        # await self._guard_last_admin(user_id, deactivating=True)
        user.is_active = False
        await self.db.commit()
        await write_audit(self.db, actor_id=actor_id, entity_type="user",
                          entity_id=user_id, action="deactivated")

    # async def _guard_last_admin(self, user_id: str, deactivating: bool = False) -> None:
    #     if deactivating:
    #         admin_count = await self.repo.count_active_admins()
    #         user = await self.repo.get_with_roles(user_id)
    #         is_admin = any(r.name == "admin" for r in user.roles)
    #         if is_admin and admin_count <= 1:
    #             raise ForbiddenOperationError("Cannot remove the last active admin")