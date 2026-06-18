"""Pytest config: set a stable test environment before app imports."""
from __future__ import annotations

import os
import tempfile

_tmp = tempfile.mkdtemp(prefix="asagent-test-")
os.environ.setdefault("DEBUG", "false")
os.environ.setdefault("SECRET_KEY", "pytest-secret-key-do-not-use-in-prod")
os.environ.setdefault("JWT_SECRET", "0123456789abcdef0123456789abcdef0123456789abcdef")
os.environ.setdefault("DATABASE_URL", f"sqlite:///{_tmp}/test.db")
os.environ.setdefault("ADMIN_PASSWORD", "pytest-admin-pw")
os.environ.setdefault("SKILLS_DIR", f"{_tmp}/skills")
os.environ.setdefault("FILES_DIR", f"{_tmp}/files")
os.environ.setdefault("SANDBOX_BACKEND", "subprocess")
