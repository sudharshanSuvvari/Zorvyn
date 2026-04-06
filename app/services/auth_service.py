# app/services/auth_service.py
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from jose import jwt, JWTError

from app.core.config import settings
from app.core.security import verify_password, create_access_token, create_refresh_token
from app.models.user import User
from app.repositories.user_repo import UserRepository
from app.schemas.auth import LoginRequest, TokenResponse, AccessTokenResponse

class AuthService:
    def __init__(self, db: AsyncSession):
        self.repo = UserRepository(User, db)

    async def login(self, payload: LoginRequest) -> TokenResponse:
        user = await self.repo.get_by_email(payload.email)

        if not user or not verify_password(payload.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        if not user.is_active:
            raise HTTPException(status_code=401, detail="Account is inactive")

        await self.repo.update_last_login(user.id)

        access_token = create_access_token({"sub": user.id, "roles": [r.name for r in user.roles]})
        refresh_token = create_refresh_token({"sub": user.id})

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    async def refresh(self, refresh_token: str) -> AccessTokenResponse:
        try:
            payload = jwt.decode(refresh_token, settings.REFRESH_SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id: str = payload.get("sub")
            if not user_id:
                raise HTTPException(status_code=401, detail="Invalid refresh token")
        except JWTError:
            raise HTTPException(status_code=401, detail="Refresh token expired or invalid")

        user = await self.repo.get_by_id(user_id)
        if not user or not user.is_active:
            raise HTTPException(status_code=401, detail="User not found or inactive")

        access_token = create_access_token({"sub": user.id, "roles": [r.name for r in user.roles]})
        return AccessTokenResponse(access_token=access_token, expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)