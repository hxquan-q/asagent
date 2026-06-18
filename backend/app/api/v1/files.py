"""Serve generated files (from save_file tool) under data/files."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from ...core.config import settings

router = APIRouter(prefix="/files", tags=["files"])


@router.get("/{name}")
def get_file(name: str) -> FileResponse:
    if "/" in name or "\\" in name or ".." in name:
        raise HTTPException(400, "invalid file name")
    path = settings.files_path / name
    if not path.is_file():
        raise HTTPException(404, "file not found")
    return FileResponse(path)
