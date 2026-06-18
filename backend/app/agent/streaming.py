"""SSE event formatting + block sink helpers for agent streaming."""
from __future__ import annotations

import json
from typing import Any

from ..content.blocks import block_to_dict
from ..content.sink import drain_sink


def sse(event: dict[str, Any]) -> str:
    """Serialise an event dict as an SSE `data:` line."""
    return "data: " + json.dumps(event, ensure_ascii=False, default=str) + "\n\n"


def block_events() -> list[dict[str, Any]]:
    """Drain the sink and return each block as a `block` event payload."""
    return [{"type": "block", "block": block_to_dict(b)} for b in drain_sink()]
