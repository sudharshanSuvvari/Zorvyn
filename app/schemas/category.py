# app/schemas/category.py
from pydantic import BaseModel, field_validator
from typing import Literal, Optional
import re

class CategoryCreate(BaseModel):
    name: str
    type: Literal["income", "expense"]
    color_hex: Optional[str] = None

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Category name cannot be blank")
        return v.strip()

    @field_validator("color_hex")
    @classmethod
    def valid_hex(cls, v: str | None) -> str | None:
        if v is not None and not re.match(r"^#[0-9A-Fa-f]{6}$", v):
            raise ValueError("color_hex must be a valid hex color e.g. #4A90E2")
        return v

class CategoryResponse(BaseModel):
    id: int
    name: str
    type: str
    color_hex: Optional[str] = None
    is_system: bool

    model_config = {"from_attributes": True}