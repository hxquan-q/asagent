from __future__ import annotations

import io
import zipfile

import pytest

from app.skills import SkillRegistry, install_zip, read_skill_file


def _zip(name: str, desc: str = "demo skill", script: str = "print('hi')") -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr(f"{name}/SKILL.md", f"---\nname: {name}\ndescription: {desc}\n---\n# {name}\n")
        zf.writestr(f"{name}/scripts/hello.py", script)
    return buf.getvalue()


def test_install_and_read(tmp_path):
    SkillRegistry._skills.clear()
    meta = install_zip(_zip("demo-skill"), tmp_path)
    SkillRegistry.register(meta)
    assert SkillRegistry.has("demo-skill")
    assert "demo-skill" in SkillRegistry.prompt_metadata()
    assert "# demo-skill" in read_skill_file.invoke({"skill": "demo-skill", "path": "SKILL.md"})


def test_name_mismatch_rejected(tmp_path):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("other/SKILL.md", "---\nname: wrong\ndescription: x\n---\n")
    with pytest.raises(ValueError):
        install_zip(buf.getvalue(), tmp_path)


def test_missing_skill_md_rejected(tmp_path):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("x/a.txt", "hi")
    with pytest.raises(ValueError):
        install_zip(buf.getvalue(), tmp_path)


def test_path_traversal_blocked(tmp_path):
    SkillRegistry._skills.clear()
    meta = install_zip(_zip("s2"), tmp_path)
    SkillRegistry.register(meta)
    with pytest.raises(Exception):  # noqa: B017
        read_skill_file.invoke({"skill": "s2", "path": "../../etc/passwd"})
