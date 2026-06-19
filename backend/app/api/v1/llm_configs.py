"""LLM config CRUD (admin) + set default."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlmodel import Session, select

from ...core.config import settings
from ...core.db import get_session
from ...core.deps import require_admin
from ...llm import PROVIDER_DEFAULTS
from ...models import LlmConfig, User

router = APIRouter(prefix="/llm_configs", tags=["llm_configs"])


class LlmConfigIn(BaseModel):
    name: str
    provider: str
    model_name: str
    api_base_url: str = ""
    api_key: str = ""
    additional_params: dict[str, Any] = {}
    is_default: bool = False
    enabled: bool = True


class LlmConfigOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    provider: str
    model_name: str
    api_base_url: str
    additional_params: dict[str, Any]
    is_default: bool
    enabled: bool
    created_at: datetime


@router.get("", response_model=list[LlmConfigOut])
def list_configs(
    admin: User = Depends(require_admin),  # noqa: ARG001
    session: Session = Depends(get_session),
) -> list[LlmConfig]:
    return session.exec(select(LlmConfig).order_by(LlmConfig.created_at.desc())).all()


@router.get("/providers")
def providers() -> dict:
    return {"providers": list(PROVIDER_DEFAULTS.keys()), "defaults": PROVIDER_DEFAULTS}


def _apply(row: LlmConfig, body: LlmConfigIn) -> None:
    row.name = body.name
    row.provider = body.provider
    row.model_name = body.model_name
    row.api_base_url = body.api_base_url
    if body.api_key:
        row.api_key_encrypted = settings.encrypt(body.api_key)
    row.additional_params = body.additional_params
    row.is_default = body.is_default
    row.enabled = body.enabled


def _set_default(session: Session, row: LlmConfig) -> None:
    if row.is_default:
        for other in session.exec(select(LlmConfig).where(LlmConfig.id != row.id)).all():
            other.is_default = False
            session.add(other)


@router.post("", response_model=LlmConfigOut)
def create_config(
    body: LlmConfigIn,
    admin: User = Depends(require_admin),  # noqa: ARG001
    session: Session = Depends(get_session),
) -> LlmConfig:
    row = LlmConfig(api_key_encrypted="")
    _apply(row, body)
    session.add(row)
    session.commit()
    session.refresh(row)
    _set_default(session, row)
    session.commit()
    session.refresh(row)
    return row


@router.put("/{cfg_id}", response_model=LlmConfigOut)
def update_config(
    cfg_id: int,
    body: LlmConfigIn,
    admin: User = Depends(require_admin),  # noqa: ARG001
    session: Session = Depends(get_session),
) -> LlmConfig:
    row = session.get(LlmConfig, cfg_id)
    if row is None:
        raise HTTPException(404, "llm_config not found")
    _apply(row, body)
    _set_default(session, row)
    session.add(row)
    session.commit()
    session.refresh(row)
    return row


@router.post("/{cfg_id}/test")
def test_config(
    cfg_id: int,
    admin: User = Depends(require_admin),  # noqa: ARG001
    session: Session = Depends(get_session),
) -> dict:
    """Send a minimal chat completion to verify the config works end-to-end."""
    from ...llm import build_from_orm, create_llm

    row = session.get(LlmConfig, cfg_id)
    if row is None:
        raise HTTPException(404, "llm_config not found")
    try:
        cfg = build_from_orm(row)
        llm = create_llm(cfg)
        resp = llm.invoke("Reply with exactly: ok")
        content = resp.content if hasattr(resp, "content") else str(resp)
        return {"ok": True, "reply": content[:200]}
    except Exception as e:
        return {"ok": False, "error": f"{type(e).__name__}: {e}"}


@router.post("/{cfg_id}/models")
def fetch_models(
    cfg_id: int,
    admin: User = Depends(require_admin),  # noqa: ARG001
    session: Session = Depends(get_session),
) -> dict:
    """Fetch available models from the provider's /models endpoint."""
    import httpx

    row = session.get(LlmConfig, cfg_id)
    if row is None:
        raise HTTPException(404, "llm_config not found")

    api_key = settings.decrypt(row.api_key_encrypted)
    base_url = (row.api_base_url or PROVIDER_DEFAULTS.get(row.provider, "")).rstrip("/")
    if not base_url:
        return {"ok": False, "error": "未配置 API Base URL", "models": []}

    try:
        resp = httpx.get(
            f"{base_url}/models",
            headers={"Authorization": f"Bearer {api_key}"} if api_key else {},
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        models = [m.get("id") or m.get("name") for m in data.get("data", data.get("models", []))]
        models = sorted([m for m in models if m])
        return {"ok": True, "models": models}
    except Exception as e:
        return {"ok": False, "error": f"{type(e).__name__}: {e}", "models": []}


@router.delete("/{cfg_id}")
def delete_config(
    cfg_id: int,
    admin: User = Depends(require_admin),  # noqa: ARG001
    session: Session = Depends(get_session),
) -> dict:
    row = session.get(LlmConfig, cfg_id)
    if row is None:
        raise HTTPException(404, "llm_config not found")
    session.delete(row)
    session.commit()
    return {"ok": True}
