"""Restricted-subprocess sandbox (always available; "soft" isolation).

Runs the script in a child process with a minimal environment, a per-run
workspace cwd, CPU/memory/file-size rlimits, and a hard timeout. This is a
practical default where Docker/Pyodide aren't available; for stronger isolation
(network off, read-only fs) use the Docker backend.
"""
from __future__ import annotations

import os
import resource
import subprocess
import sys
from pathlib import Path
from typing import Mapping

from .base import RunResult, Sandbox


class SubprocessSandbox(Sandbox):
    name = "subprocess"

    def run_script(
        self,
        script_path: Path,
        args: list[str] | None,
        workspace: Path,
        timeout: int,
        env: Mapping[str, str] | None = None,
    ) -> RunResult:
        workspace.mkdir(parents=True, exist_ok=True)
        cmd = [sys.executable, str(script_path), *(args or [])]
        clean_env = {
            "PATH": os.environ.get("PATH", ""),
            "HOME": str(workspace),
            "LANG": "C.UTF-8",
            "LC_ALL": "C.UTF-8",
            "PYTHONUNBUFFERED": "1",
            "PYTHONPATH": "",
        }
        if env:
            clean_env.update(env)

        def _set_limits() -> None:  # runs in the child
            try:
                resource.setrlimit(resource.RLIMIT_CPU, (timeout, timeout))
                resource.setrlimit(resource.RLIMIT_AS, (512 * 1024 * 1024, 512 * 1024 * 1024))
                resource.setrlimit(resource.RLIMIT_FSIZE, (50 * 1024 * 1024, 50 * 1024 * 1024))
            except (ValueError, resource.error):
                pass

        try:
            proc = subprocess.run(
                cmd,
                cwd=str(workspace),
                env=clean_env,
                capture_output=True,
                text=True,
                timeout=timeout,
                preexec_fn=_set_limits,
            )
            return RunResult(proc.returncode, proc.stdout or "", proc.stderr or "", backend=self.name)
        except subprocess.TimeoutExpired as e:
            out = e.stdout if isinstance(e.stdout, str) else ""
            err = (e.stderr if isinstance(e.stderr, str) else "") + "\n[timeout]"
            return RunResult(124, out, err, timed_out=True, backend=self.name)
