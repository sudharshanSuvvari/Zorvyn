# app/schemas/permission.py
from pydantic import BaseModel

class PermissionResponse(BaseModel):
    id: int
    resource: str
    action: str

    model_config = {"from_attributes": True}

class AssignPermissionRequest(BaseModel):
    permission_id: int