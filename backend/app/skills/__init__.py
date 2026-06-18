"""Skills subsystem (Agent Skills standard): load / register / execute."""
from .loader import install_zip, load_skill_dir, parse_frontmatter, scan_skills
from .registry import SkillMeta, SkillRegistry
from .store import list_scripts, read_text, resolve_in_skill
from .tools import SKILL_TOOLS, read_skill_file, run_skill_script

__all__ = [
    "SkillRegistry", "SkillMeta",
    "load_skill_dir", "install_zip", "scan_skills", "parse_frontmatter",
    "read_text", "resolve_in_skill", "list_scripts",
    "read_skill_file", "run_skill_script", "SKILL_TOOLS",
]
