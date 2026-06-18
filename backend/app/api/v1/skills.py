"""Skill management: upload zip (hot-load), list, enable/disable, delete, read SKILL.md."""
from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from pydantic import BaseModel, ConfigDict
from sqlmodel import Session, select

from ...core.config import settings
from ...core.db import get_session
from ...core.deps import require_admin
from ...models import Skill, User
from ...skills import SkillRegistry, install_zip, load_skill_dir

router = APIRouter(prefix="/skills", tags=["skills"])


class SkillOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int | None
    name: str
    description: str
    version: str
    license: str
    compatibility: str
    enabled: bool
    uploaded_at: datetime


@router.get("", response_model=list[SkillOut])
def list_skills(
    admin: User = Depends(require_admin),  # noqa: ARG001
    session: Session = Depends(get_session),
) -> list[Skill]:
    return session.exec(select(Skill).order_by(Skill.uploaded_at.desc())).all()


def _sync_row(row: Skill, meta) -> None:
    row.description = meta.description
    row.dir_path = str(meta.dir_path)
    row.version = meta.version
    row.license = meta.license
    row.compatibility = meta.compatibility
    row.skill_metadata = meta.metadata
    row.allowed_tools = meta.allowed_tools


@router.post("/upload", response_model=SkillOut)
def upload_skill(
    file: UploadFile = File(...),
    overwrite: bool = Query(default=False),
    admin: User = Depends(require_admin),
    session: Session = Depends(get_session),
) -> Skill:
    data = file.file.read()
    try:
        meta = install_zip(data, settings.skills_path, overwrite=overwrite)
    except ValueError as e:
        raise HTTPException(400, str(e)) from e
    SkillRegistry.register(meta)
    row = session.exec(select(Skill).where(Skill.name == meta.name)).first()
    if row is None:
        row = Skill(name=meta.name, dir_path=str(meta.dir_path), enabled=True, uploaded_by=admin.id)
    _sync_row(row, meta)
    row.enabled = True
    session.add(row)
    session.commit()
    session.refresh(row)
    return row


@router.post("/{skill_id}/enable")
def enable_skill(
    skill_id: int,
    admin: User = Depends(require_admin),  # noqa: ARG001
    session: Session = Depends(get_session),
) -> dict:
    row = session.get(Skill, skill_id)
    if row is None:
        raise HTTPException(404, "skill not found")
    row.enabled = True
    if not SkillRegistry.has(row.name):
        SkillRegistry.register(load_skill_dir(Path(row.dir_path)))
    session.add(row)
    session.commit()
    return {"ok": True}


@router.post("/{skill_id}/disable")
def disable_skill(
    skill_id: int,
    admin: User = Depends(require_admin),  # noqa: ARG001
    session: Session = Depends(get_session),
) -> dict:
    row = session.get(Skill, skill_id)
    if row is None:
        raise HTTPException(404, "skill not found")
    row.enabled = False
    SkillRegistry.unregister(row.name)
    session.add(row)
    session.commit()
    return {"ok": True}


@router.delete("/{skill_id}")
def delete_skill(
    skill_id: int,
    admin: User = Depends(require_admin),  # noqa: ARG001
    session: Session = Depends(get_session),
) -> dict:
    row = session.get(Skill, skill_id)
    if row is None:
        raise HTTPException(404, "skill not found")
    SkillRegistry.unregister(row.name)
    shutil.rmtree(row.dir_path, ignore_errors=True)
    session.delete(row)
    session.commit()
    return {"ok": True}


@router.get("/{skill_id}/skill_md")
def get_skill_md(
    skill_id: int,
    session: Session = Depends(get_session),
) -> dict:
    row = session.get(Skill, skill_id)
    if row is None:
        raise HTTPException(404, "skill not found")
    md = Path(row.dir_path) / "SKILL.md"
    if not md.is_file():
        raise HTTPException(404, "SKILL.md not found on disk")
    return {"name": row.name, "content": md.read_text(encoding="utf-8", errors="replace")}
