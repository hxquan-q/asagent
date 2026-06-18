"""API key management (admin only). The full key is shown once at creation."""
from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlmodel import Session, select

from ...core.db import get_session
from ...core.deps import require_admin
from ...core.security import generate_api_key
from ...models import ApiKey, User

router = APIRouter(prefix="/apikeys", tags=["apikeys"])


class CreateIn(BaseModel):
    name: str
    expires_at: datetime | None = None


class ApiKeyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    key_prefix: str
    enabled: bool
    last_used_at: datetime | None
    expires_at: datetime | None
    created_at: datetime


class ApiKeyCreated(ApiKeyOut):
    full_key: str  # shown once


@router.get("", response_model=list[ApiKeyOut])
def list_keys(
    admin: User = Depends(require_admin),
    session: Session = Depends(get_session),
) -> list[ApiKey]:
    return session.exec(select(ApiKey).order_by(ApiKey.created_at.desc())).all()


@router.post("", response_model=ApiKeyCreated)
def create_key(
    body: CreateIn,
    admin: User = Depends(require_admin),
    session: Session = Depends(get_session),
) -> ApiKeyCreated:
    full, prefix, key_hash = generate_api_key()
    ak = ApiKey(
        name=body.name,
        key_prefix=prefix,
        key_hash=key_hash,
        created_by=admin.id,
        expires_at=body.expires_at,
    )
    session.add(ak)
    session.commit()
    session.refresh(ak)
    return ApiKeyCreated(
        id=ak.id, name=ak.name, key_prefix=ak.key_prefix, enabled=ak.enabled,
        last_used_at=ak.last_used_at, expires_at=ak.expires_at, created_at=ak.created_at,
        full_key=full,
    )


@router.delete("/{key_id}")
def revoke_key(
    key_id: int,
    admin: User = Depends(require_admin),  # noqa: ARG001
    session: Session = Depends(get_session),
) -> dict:
    ak = session.get(ApiKey, key_id)
    if ak is None:
        raise HTTPException(404, "api key not found")
    ak.enabled = False
    session.add(ak)
    session.commit()
    return {"ok": True}
