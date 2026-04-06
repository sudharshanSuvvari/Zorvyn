# app/schemas/common.py
from pydantic import BaseModel
from typing import Generic, TypeVar

T = TypeVar("T")

class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int

class ErrorResponse(BaseModel):
    detail: str
    code: str | None = None    # machine-readable e.g. "RECORD_VOIDED"