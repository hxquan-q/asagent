"""Sandbox interface for running skill scripts."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Mapping


@dataclass
class RunResult:
    exit_code: int
    stdout: str = ""
    stderr: str = ""
    timed_out: bool = False
    backend: str = ""

    @property
    def ok(self) -> bool:
        return self.exit_code == 0 and not self.timed_out


class Sandbox:
    """Executes a skill script in an isolated environment."""

    name = "base"

    def run_script(
        self,
        script_path: Path,
        args: list[str] | None,
        workspace: Path,
        timeout: int,
        env: Mapping[str, str] | None = None,
    ) -> RunResult:
        raise NotImplementedError
