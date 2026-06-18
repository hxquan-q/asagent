"""Skill-scoped tools: read_skill_file (L2/L3 progressive disclosure) + run_skill_script (sandboxed)."""
from __future__ import annotations

import tempfile
from pathlib import Path

from langchain_core.tools import tool

from ..core.config import settings
from ..sandbox import get_sandbox
from .registry import SkillRegistry
from .store import read_text, resolve_in_skill


@tool
def read_skill_file(skill: str, path: str) -> str:
    """Read a file from an installed skill's directory.

    Use this to load a skill's SKILL.md body or its references/assets. ``path``
    is relative to the skill root (e.g. "SKILL.md", "references/FORMS.md").
    """
    meta = SkillRegistry.get(skill)
    return read_text(meta, path)


@tool
def run_skill_script(skill: str, script: str, script_args: list[str] | None = None) -> str:
    """Run a script bundled with a skill (``scripts/<script>``) in the sandbox.

    Only the script's stdout/stderr is returned — the code itself never enters
    your context.

    Args:
        skill: installed skill name.
        script: filename under the skill's ``scripts/`` directory.
        script_args: optional command-line arguments.
    """
    meta = SkillRegistry.get(skill)
    script_path = resolve_in_skill(meta, f"scripts/{script}")
    if not script_path.is_file():
        raise ValueError(f"script not found: scripts/{script}")
    with tempfile.TemporaryDirectory() as workspace:
        result = get_sandbox().run_script(
            script_path,
            script_args or [],
            Path(workspace),
            settings.SANDBOX_TIMEOUT_SECONDS,
        )
    text = f"[exit {result.exit_code} via {result.backend}]\nSTDOUT:\n{result.stdout[:4000]}"
    if result.stderr.strip():
        text += f"\nSTDERR:\n{result.stderr[:1500]}"
    if result.timed_out:
        text += "\n[timed out]"
    return text


SKILL_TOOLS = [read_skill_file, run_skill_script]

__all__ = ["read_skill_file", "run_skill_script", "SKILL_TOOLS"]
