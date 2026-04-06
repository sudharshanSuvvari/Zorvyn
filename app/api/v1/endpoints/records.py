# app/api/v1/endpoints/records.py
from fastapi import APIRouter, Depends, Query
from typing import Optional
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.db_connection import get_db
from app.api.dependencies import require_permission, get_current_user
from app.schemas.record import (
    RecordCreate, RecordUpdate, RecordResponse,
    RecordListItem, RecordFilterParams,
)
from app.schemas.common import PaginatedResponse
from app.services.record_service import RecordService
from app.models.user import User

record_router = APIRouter()

@record_router.get("", response_model=PaginatedResponse[RecordListItem])
async def list_records(
    type: Optional[str]     = Query(None, pattern="^(income|expense)$"),
    category_id: Optional[int] = Query(None),
    status: Optional[str]   = Query(None, pattern="^(draft|posted|void)$"),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date]   = Query(None),
    page: int               = Query(1, ge=1),
    page_size: int          = Query(50, ge=1, le=100),
    sort: str               = Query("record_date:desc"),
    current_user: User = Depends(require_permission("financial_records", "read")),
    db: AsyncSession = Depends(get_db),
):
    filters = RecordFilterParams(
        type=type, category_id=category_id, status=status,
        date_from=date_from, date_to=date_to,
        page=page, page_size=page_size, sort=sort,
    )
    return await RecordService(db).list_records(filters)

@record_router.get("/{record_id}", response_model=RecordResponse)
async def get_record(
    record_id: str,
    current_user: User = Depends(require_permission("financial_records", "read")),
    db: AsyncSession = Depends(get_db),
):
    return await RecordService(db).get_record(record_id)

@record_router.post("", response_model=RecordResponse, status_code=201)
async def create_record(
    payload: RecordCreate,
    current_user: User = Depends(require_permission("financial_records", "create")),
    db: AsyncSession = Depends(get_db),
):
    return await RecordService(db).create_record(payload, actor_id=current_user.id)

@record_router.patch("/{record_id}", response_model=RecordResponse)
async def update_record(
    record_id: str,
    payload: RecordUpdate,
    current_user: User = Depends(require_permission("financial_records", "update")),
    db: AsyncSession = Depends(get_db),
):
    return await RecordService(db).update_record(record_id, payload, actor_id=current_user.id)

@record_router.delete("/{record_id}", status_code=204)
async def delete_record(
    record_id: str,
    current_user: User = Depends(require_permission("financial_records", "delete")),
    db: AsyncSession = Depends(get_db),
):
    await RecordService(db).delete_record(record_id, actor_id=current_user.id)

@record_router.get("/{record_id}/history", response_model=list[dict])
async def get_record_history(
    record_id: str,
    current_user: User = Depends(require_permission("financial_records", "read_history")),
    db: AsyncSession = Depends(get_db),
):
    return await RecordService(db).get_record_history(record_id)