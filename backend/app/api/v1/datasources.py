"""Datasource CRUD (admin) + connection test."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlmodel import Session, select

from ...core.config import settings
from ...core.db import get_session
from ...core.deps import require_admin
from ...datasources import introspect, manager
from ...models import Datasource, User

router = APIRouter(prefix="/datasources", tags=["datasources"])


class DatasourceIn(BaseModel):
    name: str
    type: str = "postgres"
    host: str
    port: int = 5432
    db: str
    username: str
    password: str = ""
    options: dict[str, Any] = {}
    enabled: bool = True


class DatasourceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    type: str
    host: str
    port: int
    db: str
    username: str
    options: dict[str, Any]
    enabled: bool
    created_at: datetime


@router.get("", response_model=list[DatasourceOut])
def list_datasources(
    admin: User = Depends(require_admin),  # noqa: ARG001
    session: Session = Depends(get_session),
) -> list[Datasource]:
    return session.exec(select(Datasource).order_by(Datasource.created_at.desc())).all()


def _build(row_in: DatasourceIn) -> Datasource:
    return Datasource(
        name=row_in.name, type=row_in.type, host=row_in.host, port=row_in.port,
        db=row_in.db, username=row_in.username,
        password_encrypted=settings.encrypt(row_in.password),
        options=row_in.options, enabled=row_in.enabled,
    )


@router.post("", response_model=DatasourceOut)
def create_datasource(
    body: DatasourceIn,
    admin: User = Depends(require_admin),  # noqa: ARG001
    session: Session = Depends(get_session),
) -> Datasource:
    ds = _build(body)
    session.add(ds)
    session.commit()
    session.refresh(ds)
    return ds


@router.put("/{ds_id}", response_model=DatasourceOut)
def update_datasource(
    ds_id: int,
    body: DatasourceIn,
    admin: User = Depends(require_admin),  # noqa: ARG001
    session: Session = Depends(get_session),
) -> Datasource:
    ds = session.get(Datasource, ds_id)
    if ds is None:
        raise HTTPException(404, "datasource not found")
    ds.name = body.name
    ds.type = body.type
    ds.host = body.host
    ds.port = body.port
    ds.db = body.db
    ds.username = body.username
    if body.password:
        ds.password_encrypted = settings.encrypt(body.password)
    ds.options = body.options
    ds.enabled = body.enabled
    session.add(ds)
    session.commit()
    session.refresh(ds)
    manager.drop_datasource_engine(ds.id)
    return ds


@router.delete("/{ds_id}")
def delete_datasource(
    ds_id: int,
    admin: User = Depends(require_admin),  # noqa: ARG001
    session: Session = Depends(get_session),
) -> dict:
    ds = session.get(Datasource, ds_id)
    if ds is None:
        raise HTTPException(404, "datasource not found")
    manager.drop_datasource_engine(ds.id)
    session.delete(ds)
    session.commit()
    return {"ok": True}


@router.post("/{ds_id}/test")
def test_datasource(
    ds_id: int,
    admin: User = Depends(require_admin),  # noqa: ARG001
    session: Session = Depends(get_session),
) -> dict:
    ds = session.get(Datasource, ds_id)
    if ds is None:
        raise HTTPException(404, "datasource not found")
    manager.drop_datasource_engine(ds.id)
    try:
        summary = introspect.schema_summary_from_engine(manager.get_datasource_engine(ds), max_tables=5)
        return {"ok": True, "tables_preview": summary[:300]}
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "error": str(e)}
