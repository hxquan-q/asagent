"""Security primitives: password hashing (bcrypt), JWT (PyJWT, HS256), API keys.

At-rest secret encryption for LLM keys / datasource passwords lives on
``settings.encrypt`` / ``settings.decrypt`` (Fernet) in ``app.core.config``.
"""
from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
import jwt

from .config import settings


# ---------- passwords ----------
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except (ValueError, TypeError):
        return False


# ---------- JWT ----------
def create_access_token(subject: str, expires_minutes: Optional[int] = None) -> str:
    now = datetime.now(timezone.utc)
    exp_delta = timedelta(minutes=expires_minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": subject, "iat": now, "exp": now + exp_delta}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    """Decode + verify. Raises ``jwt.PyJWTError`` on invalid/expired tokens."""
    return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])


# ---------- API keys ----------
def generate_api_key() -> tuple[str, str, str]:
    """Return (full_key, prefix, key_hash).

    The full key is shown once at creation; only prefix + hash are stored.
    """
    raw = secrets.token_urlsafe(32)
    full = f"{settings.API_KEY_PREFIX}_{raw}"
    return full, full[:12], hash_api_key(full)


def hash_api_key(full_key: str) -> str:
    return hashlib.sha256(full_key.encode("utf-8")).hexdigest()
