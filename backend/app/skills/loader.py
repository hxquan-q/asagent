"""Skill loading: zip install, SKILL.md frontmatter parsing, startup scan.

Implements the Agent Skills spec (agentskills.io): a skill is a directory with
``SKILL.md`` (YAML frontmatter: required ``name`` + ``description``) plus
optional ``scripts/`` / ``references/`` / ``assets/``.
"""
from __future__ import annotations

import io
import logging
import re
import shutil
import tempfile
import zipfile
from pathlib import Path

import yaml

from .registry import SkillMeta, SkillRegistry

log = logging.getLogger("asagent")

# name: 1-64 chars, lowercase alnum + hyphens, no leading/trailing/double hyphens
_NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", re.DOTALL)


def parse_frontmatter(text: str) -> tuple[dict, str]:
    m = _FRONTMATTER_RE.match(text)
    if not m:
        raise ValueError("SKILL.md must begin with YAML frontmatter ('---\\n...\\n---')")
    fm = yaml.safe_load(m.group(1)) or {}
    if not isinstance(fm, dict):
        raise ValueError("SKILL.md frontmatter must be a YAML mapping")
    return fm, m.group(2)


def _validate_name(name: str, dir_name: str) -> str:
    name = (name or "").strip()
    if not _NAME_RE.match(name) or not (1 <= len(name) <= 64):
        raise ValueError(f"invalid skill name: {name!r} (lowercase alnum/hyphens, 1-64 chars)")
    if name != dir_name:
        raise ValueError(f"skill name {name!r} must equal its directory name {dir_name!r}")
    return name


def load_skill_dir(skill_dir: Path) -> SkillMeta:
    skill_dir = skill_dir.resolve()
    md = skill_dir / "SKILL.md"
    if not md.is_file():
        raise ValueError("SKILL.md missing")
    fm, body = parse_frontmatter(md.read_text(encoding="utf-8"))
    name = _validate_name(str(fm.get("name", "")), skill_dir.name)
    description = str(fm.get("description", "")).strip()
    if not description or len(description) > 1024:
        raise ValueError("description is required (1-1024 chars)")
    return SkillMeta(
        name=name,
        description=description,
        dir_path=skill_dir,
        body=body,
        license=str(fm.get("license", "") or ""),
        compatibility=str(fm.get("compatibility", "") or ""),
        metadata=fm.get("metadata") or {},
        allowed_tools=str(fm.get("allowed-tools", "") or ""),
        version=str(fm.get("version", "1.0.0") or "1.0.0"),
    )


def install_zip(zip_bytes: bytes, skills_root: Path, overwrite: bool = False) -> SkillMeta:
    """Validate + unpack a skill zip into ``skills_root`` and return its metadata."""
    skills_root.mkdir(parents=True, exist_ok=True)
    try:
        zf = zipfile.ZipFile(io.BytesIO(zip_bytes))
    except zipfile.BadZipFile as e:
        raise ValueError(f"not a valid zip: {e}") from e

    members = [n for n in zf.namelist() if not n.endswith("/")]
    # block absolute paths and parent escapes (zip-slip)
    for n in members:
        if n.startswith("/") or ".." in Path(n).parts:
            raise ValueError(f"unsafe zip entry: {n}")

    skill_md = next((n for n in members if n.endswith("SKILL.md")), None)
    if not skill_md:
        raise ValueError("zip contains no SKILL.md")
    parts = Path(skill_md).parts
    if len(parts) < 2:
        raise ValueError("SKILL.md must live inside a top-level directory named after the skill")

    with tempfile.TemporaryDirectory() as td:
        zf.extractall(td)
        extracted = Path(td) / parts[0]
        meta = load_skill_dir(extracted)  # validates name == dir + frontmatter
        dest = skills_root / meta.name
        if dest.exists():
            if not overwrite:
                raise ValueError(f"skill '{meta.name}' already exists; use overwrite")
            shutil.rmtree(dest)
        shutil.move(str(extracted), str(dest))
        return load_skill_dir(dest)


def scan_skills(skills_root: Path) -> list[SkillMeta]:
    """Discover + register every skill dir under ``skills_root`` (startup)."""
    metas: list[SkillMeta] = []
    if not skills_root.exists():
        return metas
    for d in sorted(skills_root.iterdir()):
        if not d.is_dir() or not (d / "SKILL.md").exists():
            continue
        try:
            meta = load_skill_dir(d)
            SkillRegistry.register(meta)
            metas.append(meta)
            log.info("loaded skill '%s'", meta.name)
        except Exception as e:  # noqa: BLE001
            log.warning("skipping skill %s: %s", d.name, e)
    return metas
