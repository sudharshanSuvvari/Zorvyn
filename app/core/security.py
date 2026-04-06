# app/core/jwt.py

from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

import bcrypt
from jose import jwt, JWTError, ExpiredSignatureError
from passlib.context import CryptContext

from app.core.config import settings
from app.core.logging import get_logger

from app.core.exceptions import TokenInvalidError, TokenExpiredError
logger = get_logger()


# ── Token creation ────────────────────────────────────────────────────────────

def create_access_token(
    user_details: Dict[str, Any],
    extra_claims: Optional[Dict[str, Any]] = None,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Create a short-lived access token.

    Includes:
      sub   — user ID (standard JWT subject claim)
      roles — list of role names, used by require_permission() dependency
      type  — "access", so the decode step can reject refresh tokens
              passed to protected endpoints
      exp   — expiry timestamp
    """
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    payload: Dict[str, Any] = {
        "sub":   user_details.get("sub"),
        "roles": user_details.get("roles"),
        "type":  "access",
        "exp":   expire,
        "iat":   datetime.now(timezone.utc),   # issued-at, useful for audit
    }

    if extra_claims:
        payload.update(extra_claims)

    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    logger.debug("access token created", extra={"user_id": user_details.get("sub"), "expires": expire.isoformat()})
    return token


def create_refresh_token(
    user_details: Dict[str, Any],
    expires_delta: Optional[timedelta] = None,   # fixed typo: expire_delata → expires_delta
) -> str:
    """
    Create a long-lived refresh token.

    Deliberately excludes roles — roles are re-fetched from the DB
    when the refresh is exchanged, so stale role data never persists
    inside a token across role changes.

    Uses a separate secret (REFRESH_SECRET_KEY) so a leaked access
    token secret cannot be used to forge refresh tokens.
    """
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )

    payload: Dict[str, Any] = {
        "sub":  user_details.get("sub"),
        "type": "refresh",          # guards against using refresh token as access token
        "exp":  expire,
        "iat":  datetime.now(timezone.utc),
    }

    token = jwt.encode(payload, settings.REFRESH_SECRET_KEY, algorithm=settings.ALGORITHM)
    logger.debug("refresh token created", extra={"user_id": user_details.get("sub"), "expires": expire.isoformat()})
    return token


# ── Token decoding ────────────────────────────────────────────────────────────

def decode_access_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate an access token.

    Raises:
      TokenExpiredError   — token is structurally valid but past expiry
      TokenInvalidError   — token is malformed, wrong secret, or wrong type
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
    except ExpiredSignatureError:
        logger.info("access token expired")
        raise TokenExpiredError("Access token has expired")
    except JWTError as exc:
        logger.warning("access token decode failed", extra={"error": str(exc)})
        raise TokenInvalidError("Access token is invalid")

    if payload.get("type") != "access":
        raise TokenInvalidError("Token type is not 'access'")

    return payload


def decode_refresh_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate a refresh token.

    """
    try:
        payload = jwt.decode(
            token,
            settings.REFRESH_SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
    except ExpiredSignatureError:
        logger.info("refresh token expired")
        raise TokenExpiredError("Refresh token has expired, please log in again")
    except JWTError as exc:
        logger.warning("refresh token decode failed", extra={"error": str(exc)})
        raise TokenInvalidError("Refresh token is invalid")

    if payload.get("type") != "refresh":
        raise TokenInvalidError("Token type is not 'refresh'")

    return payload


# ── Password hashing ──────────────────────────────────────────────────────────
import bcrypt

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password)