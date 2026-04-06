# app/schemas/record.py
from pydantic import BaseModel, field_validator, model_validator
from typing import Literal, Optional
from datetime import date, datetime
from decimal import Decimal
from app.schemas.category import CategoryResponse
from app.schemas.user import UserListResponse

RecordType = Literal["income", "expense"]
RecordStatus = Literal["draft", "posted", "void"]

class RecordCreate(BaseModel):
    type: RecordType
    amount: Decimal
    currency: str = "USD"
    category_id: int
    record_date: date
    description: Optional[str] = None
    status: RecordStatus = "posted"

    @field_validator("amount")
    @classmethod
    def amount_positive(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("Amount must be greater than zero")
        if v > Decimal("999999999.99"):
            raise ValueError("Amount exceeds maximum allowed value")
        return round(v, 2)

    @field_validator("currency")
    @classmethod
    def valid_currency(cls, v: str) -> str:
        allowed = {"USD", "EUR", "GBP", "INR", "JPY", "AUD", "CAD"}
        if v.upper() not in allowed:
            raise ValueError(f"Currency must be one of {allowed}")
        return v.upper()

    @field_validator("description")
    @classmethod
    def description_length(cls, v: str | None) -> str | None:
        if v and len(v) > 500:
            raise ValueError("Description cannot exceed 500 characters")
        return v

    @field_validator("record_date")
    @classmethod
    def not_future_date(cls, v: date) -> date:
        if v > date.today():
            raise ValueError("record_date cannot be in the future")
        return v

class RecordUpdate(BaseModel):
    amount: Optional[Decimal] = None
    category_id: Optional[int] = None
    description: Optional[str] = None
    record_date: Optional[date] = None
    status: Optional[RecordStatus] = None

    @field_validator("amount")
    @classmethod
    def amount_positive(cls, v: Decimal | None) -> Decimal | None:
        if v is not None and v <= 0:
            raise ValueError("Amount must be greater than zero")
        return round(v, 2) if v else v

class RecordResponse(BaseModel):
    id: str
    type: str
    amount: Decimal
    currency: str
    category: CategoryResponse
    description: Optional[str]
    record_date: date
    status: str
    created_by: UserListResponse
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

class RecordListItem(BaseModel):
    id: str
    type: str
    amount: Decimal
    currency: str
    category: CategoryResponse
    record_date: date
    status: str
    description: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}

class RecordFilterParams(BaseModel):
    type: Optional[RecordType] = None
    category_id: Optional[int] = None
    status: Optional[RecordStatus] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    page: int = 1
    page_size: int = 50
    sort: str = "record_date:desc"

    @model_validator(mode="after")
    def date_range_valid(self) -> "RecordFilterParams":
        if self.date_from and self.date_to and self.date_from > self.date_to:
            raise ValueError("date_from cannot be after date_to")
        return self

    @field_validator("sort")
    @classmethod
    def valid_sort(cls, v: str) -> str:
        allowed = {"record_date:asc", "record_date:desc", "amount:asc", "amount:desc", "created_at:desc"}
        if v not in allowed:
            raise ValueError(f"sort must be one of {allowed}")
        return v

    @field_validator("page_size")
    @classmethod
    def page_size_limit(cls, v: int) -> int:
        if v > 100:
            raise ValueError("page_size cannot exceed 100")
        return v