"""Docker sandbox — strong isolation: no network, read-only fs, capped resources.

Requires the ``asagent-sandbox`` image (see deploy/sandbox.Dockerfile). The
script's ``scripts/`` dir is mounted read-only at ``/skill``; a fresh workspace
is mounted read-write at ``/work`` (cwd).
"""
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Mapping

from ..core.config import settings
from .base import RunResult, Sandbox


class DockerSandbox(Sandbox):
    name = "docker"

    def run_script(
        self,
        script_path: Path,
        args: list[str] | None,
        workspace: Path,
        timeout: int,
        env: Mapping[str, str] | None = None,
    ) -> RunResult:
        workspace.mkdir(parents=True, exist_ok=True)
        scripts_dir = script_path.parent.resolve()
        image = settings.SANDBOX_DOCKER_IMAGE
        cmd = [
            "docker", "run", "--rm",
            "--network=none",
            "--read-only",
            "--tmpfs", "/tmp:rw",
            "--memory=512m",
            "--pids-limit=64",
            "--cap-drop=ALL",
            "--security-opt=no-new-privileges",
            "-v", f"{workspace.resolve()}:/work:rw",
            "-v", f"{scripts_dir}:/skill:ro",
            "-w", "/work",
            image, "python", f"/skill/{script_path.name}",
            *(args or []),
        ]
        full_env = None
        if env:
            full_env = []
            for k, v in env.items():
                full_env += ["-e", f"{k}={v}"]
            cmd[1:1] = full_env
        try:
            proc = subprocess.run(
                cmd, capture_output=True, text=True, timeout=timeout + 5
            )
            return RunResult(proc.returncode, proc.stdout or "", proc.stderr or "", backend=self.name)
        except subprocess.TimeoutExpired:
            return RunResult(124, "", "[timeout]", timed_out=True, backend=self.name)
