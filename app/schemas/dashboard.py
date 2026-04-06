# app/schemas/dashboard.py
from pydantic import BaseModel
from typing import Optional
from datetime import date
from decimal import Decimal

class DateRangeParams(BaseModel):
    date_from: Optional[date] = None
    date_to: Optional[date] = None

class SummaryResponse(BaseModel):
    total_income: Decimal
    total_expenses: Decimal
    net_balance: Decimal
    currency: str
    record_count: int
    period: dict                    # {"from": date, "to": date}

class CategoryTotalItem(BaseModel):
    category_id: int
    category_name: str
    total: Decimal
    percentage: float
    count: int

class TrendPoint(BaseModel):
    period: str                     # "2025-01" or "2025-W04"
    income: Decimal
    expenses: Decimal
    net: Decimal

class RecentActivityItem(BaseModel):
    id: str
    type: str
    amount: Decimal
    currency: str
    category_name: str
    record_date: date
    description: Optional[str]