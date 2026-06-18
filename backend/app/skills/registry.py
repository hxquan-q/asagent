"""In-memory skill registry (borrowed from vanna's registry pattern)."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class SkillMeta:
    name: str
    description: str
    dir_path: Path
    body: str = ""
    license: str = ""
    compatibility: str = ""
    metadata: dict = field(default_factory=dict)
    allowed_tools: str = ""
    version: str = "1.0.0"


class SkillRegistry:
    _skills: dict[str, SkillMeta] = {}

    @classmethod
    def register(cls, meta: SkillMeta) -> None:
        cls._skills[meta.name] = meta

    @classmethod
    def unregister(cls, name: str) -> None:
        cls._skills.pop(name, None)

    @classmethod
    def get(cls, name: str) -> SkillMeta:
        meta = cls._skills.get(name)
        if meta is None:
            raise KeyError(f"skill '{name}' not loaded")
        return meta

    @classmethod
    def has(cls, name: str) -> bool:
        return name in cls._skills

    @classmethod
    def names(cls) -> list[str]:
        return list(cls._skills)

    @classmethod
    def all(cls) -> list[SkillMeta]:
        return list(cls._skills.values())

    @classmethod
    def prompt_metadata(cls) -> str:
        """Level-1 progressive disclosure: name + description of all loaded skills."""
        skills = cls._skills.values()
        if not skills:
            return "(no skills installed)"
        return "\n".join(f"- {m.name}: {m.description}" for m in skills)
