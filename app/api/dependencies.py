'''
  extract_token, get_current_user, require_permission
'''

# app/core/security.py
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.db_connection import get_db
from app.core.exceptions import ForbiddenOperationError
from app.models.user import User
from app.repositories.user_repo import UserRepository
from app.core.security import decode_access_token

bearer_scheme = HTTPBearer()

# ── Layer 1: extract & decode the JWT token ───────────────────────────────────

from app.core.security import decode_access_token, TokenExpiredError, TokenInvalidError

async def extract_token(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict:
    try:
        return decode_access_token(credentials.credentials)
    except TokenExpiredError:
        raise HTTPException(status_code=401, detail="Access token has expired")
    except TokenInvalidError:
        raise HTTPException(status_code=401, detail="Access token is invalid")

# ── Layer 2: hydrate the user from DB, enforce is_active ─────────────────────

async def get_current_user(
    payload: dict = Depends(extract_token),
    db: AsyncSession = Depends(get_db),
) -> User:
    user_id = payload["sub"]
    repo = UserRepository(User, db)
    user = await repo.get_with_roles(user_id)   # eagerly loads roles + permissions

    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=401, detail="Account is inactive")

    return user


# ── Layer 3: permission gate — the factory that routes inject ─────────────────

def require_permission(resource: str, action: str):

    async def _check(current_user: User = Depends(get_current_user)) -> User:
        for user_role in current_user.roles:

            for perm in user_role.permissions:
                if perm.resource == resource and perm.action == action:
                    return current_user

        raise ForbiddenOperationError("You do not have the access to the do the operation")

    return _check