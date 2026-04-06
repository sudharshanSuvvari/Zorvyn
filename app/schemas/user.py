# app/schemas/user.py
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime
from app.schemas.role import RoleResponse

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role_ids: list[int]

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        print("Password validation passed")
        return v

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Full name cannot be blank")
        return v.strip()

    @field_validator("role_ids")
    @classmethod
    def roles_not_empty(cls, v: list[int]) -> list[int]:
        if not v:
            raise ValueError("At least one role must be assigned")
        return v

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    role_ids: Optional[list[int]] = None

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    is_active: bool
    roles: list[RoleResponse]
    created_at: datetime
    last_login_at: Optional[datetime] = None

    model_config = {"from_attributes": True}

class UserListResponse(BaseModel):
    id: str
    email: str
    full_name: str
    is_active: bool
    roles: list[RoleResponse]
    created_at: datetime

    model_config = {"from_attributes": True}