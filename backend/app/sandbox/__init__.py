"""Sandbox subsystem: pick a backend (docker > subprocess), with graceful fallback."""
from __future__ import annotations

import logging
import shutil

from ..core.config import settings
from .base import RunResult, Sandbox
from .docker import DockerSandbox
from .subprocess import SubprocessSandbox

__all__ = ["Sandbox", "RunResult", "get_sandbox"]

_instance: Sandbox | None = None


def get_sandbox() -> Sandbox:
    """Return the configured sandbox, falling back to subprocess if unavailable."""
    global _instance
    if _instance is not None:
        return _instance

    log = logging.getLogger("asagent")
    backend = (settings.SANDBOX_BACKEND or "subprocess").lower()
    if backend == "docker" and shutil.which("docker"):
        _instance = DockerSandbox()
        log.info("sandbox backend: docker")
    else:
        if backend == "docker":
            log.warning("docker sandbox requested but 'docker' not found; using subprocess")
        _instance = SubprocessSandbox()
        log.info("sandbox backend: subprocess")
    return _instance


def reset_sandbox() -> None:
    global _instance
    _instance = None
