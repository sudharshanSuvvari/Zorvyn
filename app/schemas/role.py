# app/schemas/role.py
from pydantic import BaseModel
from app.schemas.permission import PermissionResponse

class RoleResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
    permissions: list[PermissionResponse] = []

    model_config = {"from_attributes": True}