"""Per-invocation block sink.

Tools that produce rich UI (tables, charts, files, ...) call ``emit_block``;
the runtime drains the sink after each tool call and streams blocks to the
client as SSE ``block`` events. The agent itself receives only a condensed
textual summary, keeping its context small (progressive disclosure of output).
"""
from __future__ import annotations

from contextvars import ContextVar
from typing import Any

_sink: ContextVar[list[Any] | None] = ContextVar("block_sink", default=None)


def new_sink() -> list[Any]:
    """Start a fresh sink for the current chat invocation."""
    sink: list[Any] = []
    _sink.set(sink)
    return sink


def emit_block(block: Any) -> None:
    """Append a content block if a sink is active; no-op otherwise."""
    sink = _sink.get()
    if sink is not None:
        sink.append(block)


def drain_sink() -> list[Any]:
    """Return and clear all blocks emitted since the last drain."""
    sink = _sink.get()
    if sink is None:
        return []
    out = list(sink)
    sink.clear()
    return out
