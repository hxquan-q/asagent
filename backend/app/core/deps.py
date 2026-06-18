"""Auth dependencies: JWT (console) + API key (external API)."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from fastapi import Depends, Header, HTTPException
from sqlmodel import Session, select

from ..models import ApiKey, User
from .db import get_session
from .security import decode_access_token, hash_api_key


def _now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class Principal:
    """An authenticated caller — either a console user (JWT) or an API key."""

    user: User | None = None
    api_key: ApiKey | None = None

    @property
    def display(self) -> str:
        if self.user:
            return f"user:{self.user.username}"
        if self.api_key:
            return f"apikey:{self.api_key.name}"
        return "?"


def get_current_user(
    authorization: str | None = Header(default=None),
    session: Session = Depends(get_session),
) -> User:
    """Require a console JWT bearer token."""
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(401, "missing Authorization bearer token")
    token = authorization.split(" ", 1)[1].strip()
    try:
        payload = decode_access_token(token)
    except Exception as e:  # noqa: BLE001
        raise HTTPException(401, f"invalid or expired token: {e}") from e
    user = session.exec(select(User).where(User.username == payload.get("sub"))).first()
    if user is None:
        raise HTTPException(401, "user not found")
    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    if not user.is_admin:
        raise HTTPException(403, "admin privileges required")
    return user


def get_principal(
    authorization: str | None = Header(default=None),
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    session: Session = Depends(get_session),
) -> Principal:
    """Accept either a console JWT or an external API key (for /chat)."""
    if x_api_key:
        ak = session.exec(
            select(ApiKey).where(ApiKey.key_hash == hash_api_key(x_api_key), ApiKey.enabled == True)  # noqa: E712
        ).first()
        if ak is None:
            raise HTTPException(401, "invalid api key")
        if ak.expires_at and ak.expires_at < _now():
            raise HTTPException(401, "api key expired")
        ak.last_used_at = _now()
        session.add(ak)
        session.commit()
        return Principal(api_key=ak)

    if authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1].strip()
        try:
            payload = decode_access_token(token)
        except Exception as e:  # noqa: BLE001
            raise HTTPException(401, f"invalid token: {e}") from e
        user = session.exec(select(User).where(User.username == payload.get("sub"))).first()
        if user is None:
            raise HTTPException(401, "user not found")
        return Principal(user=user)

    raise HTTPException(401, "no credentials (Authorization: Bearer <jwt> or X-API-Key)")
