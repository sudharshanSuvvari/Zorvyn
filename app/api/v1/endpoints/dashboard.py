# app/api/v1/endpoints/dashboard.py
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from typing import Literal, Optional
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.db_connection import get_db
from app.api.dependencies import require_permission
from app.schemas.dashboard import SummaryResponse, CategoryTotalItem, TrendPoint, RecentActivityItem
from app.services.dashboard_service import DashboardService
from app.models.user import User

dashboard_router = APIRouter()

@dashboard_router.get("/summary", response_model=SummaryResponse)
async def get_summary(
    date_from: Optional[date] = Query(None),
    date_to: Optional[date]   = Query(None),
    current_user: User = Depends(require_permission("analytics", "read")),
    db: AsyncSession = Depends(get_db),
):
    return await DashboardService(db).get_summary(date_from, date_to)

@dashboard_router.get("/by-category", response_model=list[CategoryTotalItem])
async def get_by_category(
    date_from: Optional[date] = Query(None),
    date_to: Optional[date]   = Query(None),
    type: Optional[str] = Query(None, pattern="^(income|expense)$"),
    current_user: User = Depends(require_permission("analytics", "read")),
    db: AsyncSession = Depends(get_db),
):
    return await DashboardService(db).get_by_category(date_from, date_to, type)

@dashboard_router.get("/trends", response_model=list[TrendPoint])
async def get_trends(
    granularity: Literal["monthly", "weekly"] = Query("monthly"),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date]   = Query(None),
    current_user: User = Depends(require_permission("analytics", "read_trends")),
    db: AsyncSession = Depends(get_db),
):
    return await DashboardService(db).get_trends(granularity, date_from, date_to)

@dashboard_router.get("/recent-activity", response_model=list[RecentActivityItem])
async def get_recent_activity(
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(require_permission("analytics", "read")),
    db: AsyncSession = Depends(get_db),
):
    return await DashboardService(db).get_recent_activity(limit)

@dashboard_router.get("/export")
async def export_csv(
    date_from: Optional[date] = Query(None),
    date_to: Optional[date]   = Query(None),
    type: Optional[str] = Query(None, pattern="^(income|expense)$"),
    current_user: User = Depends(require_permission("analytics", "export")),
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    return await DashboardService(db).export_csv(date_from, date_to, type)