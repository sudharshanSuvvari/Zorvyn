from fastapi import APIRouter
from app.api.v1.endpoints.auth import auth_router
from app.api.v1.endpoints.user import user_router
from app.api.v1.endpoints.category import category_router
from app.api.v1.endpoints.roles import role_router
from app.api.v1.endpoints.dashboard import dashboard_router
from app.api.v1.endpoints.records import record_router

v1_router = APIRouter()

v1_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
v1_router.include_router(user_router, prefix="/user", tags=["User"])
v1_router.include_router(category_router, prefix="/categories", tags=["Categories"])
v1_router.include_router(role_router, prefix="/roles", tags=["Roles"])
v1_router.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard"])
v1_router.include_router(record_router,prefix="/records", tags=["Financial Records"])