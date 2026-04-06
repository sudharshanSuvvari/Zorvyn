# app/api/v1/endpoints/users.py
from fastapi import APIRouter, Depends, Query
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.db_connection import get_db
from app.api.dependencies import require_permission, get_current_user
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserListResponse
from app.schemas.common import PaginatedResponse
from app.services.user_service import UserService
from app.models.user import User

user_router = APIRouter()

@user_router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@user_router.get("", response_model=PaginatedResponse[UserListResponse])
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    is_active: Optional[bool] = Query(None),
    role: Optional[str] = Query(None),
    current_user: User = Depends(require_permission("users", "list")),
    db: AsyncSession = Depends(get_db),
):
    return await UserService(db).list_users(page, page_size, is_active, role)

@user_router.post("", response_model=UserResponse, status_code=201)
async def create_user(
    payload: UserCreate,
    # current_user: User = Depends(require_permission("users", "create")),
    db: AsyncSession = Depends(get_db),
):
    return await UserService(db).create_user(payload, actor_id=1)

@user_router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    payload: UserUpdate,
    current_user: User = Depends(require_permission("users", "update")),
    db: AsyncSession = Depends(get_db),
):
    return await UserService(db).update_user(user_id, payload, actor_id=current_user.id)

@user_router.delete("/{user_id}", status_code=204)
async def delete_user(
    user_id: str,
    current_user: User = Depends(require_permission("users", "delete")),
    db: AsyncSession = Depends(get_db),
):
    await UserService(db).delete_user(user_id, actor_id=current_user.id)