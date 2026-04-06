# app/api/v1/endpoints/categories.py
from fastapi import APIRouter, Depends, Query
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.db_connection import get_db
from app.api.dependencies import require_permission, get_current_user
from app.schemas.category import CategoryCreate, CategoryResponse
from app.services.category_service import CategoryService
from app.models.user import User

category_router = APIRouter()

@category_router.get("", response_model=list[CategoryResponse])
async def list_categories(
    type: Optional[str] = Query(None, pattern="^(income|expense)$"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await CategoryService(db).list_categories(type_filter=type)

@category_router.post("", response_model=CategoryResponse, status_code=201)
async def create_category(
    payload: CategoryCreate,
    current_user: User = Depends(require_permission("categories", "create")),
    db: AsyncSession = Depends(get_db),
):
    return await CategoryService(db).create_category(payload)

@category_router.delete("/{category_id}", status_code=204)
async def delete_category(
    category_id: int,
    current_user: User = Depends(require_permission("categories", "delete")),
    db: AsyncSession = Depends(get_db),
):
    await CategoryService(db).delete_category(category_id)