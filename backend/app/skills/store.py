"""Safe filesystem access scoped to a single skill directory."""
from __future__ import annotations

from pathlib import Path

from .registry import SkillMeta


def resolve_in_skill(meta: SkillMeta, rel_path: str) -> Path:
    """Resolve ``rel_path`` against the skill root, refusing path escapes."""
    base = meta.dir_path.resolve()
    full = (base / rel_path).resolve()
    if full != base and base not in full.parents:
        raise ValueError(f"path escapes skill directory: {rel_path}")
    return full


def read_text(meta: SkillMeta, rel_path: str, limit: int = 20000) -> str:
    full = resolve_in_skill(meta, rel_path)
    if not full.is_file():
        raise ValueError(f"not a file: {rel_path}")
    return full.read_text(encoding="utf-8", errors="replace")[:limit]


def list_scripts(meta: SkillMeta) -> list[str]:
    scripts_dir = meta.dir_path / "scripts"
    if not scripts_dir.is_dir():
        return []
    return sorted(p.name for p in scripts_dir.iterdir() if p.is_file())
