# app/api/v1/endpoints/auth.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.db_connection import get_db
from app.schemas.auth import LoginRequest, TokenResponse, RefreshRequest, AccessTokenResponse
from app.services.auth_service import AuthService

auth_router = APIRouter()

@auth_router.post("/login", response_model=TokenResponse, status_code=200)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    return await AuthService(db).login(payload)

@auth_router.post("/refresh", response_model=AccessTokenResponse, status_code=200)
async def refresh_token(payload: RefreshRequest, db: AsyncSession = Depends(get_db)):
    return await AuthService(db).refresh(payload.refresh_token)