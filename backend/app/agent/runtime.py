"""Agent streaming runtime.

Yields a sequence of event dicts (`token`, `tool_start`, `tool_end`, `block`,
`done`, `error`) as a LangGraph ReAct agent runs. Rich content blocks produced
by tools are drained from the sink and emitted as `block` events; the agent
itself sees only condensed text (progressive disclosure of output).

The whole agent loop runs in ONE dedicated worker thread and events are handed
to the caller via a thread-safe queue. This keeps the block-sink / datasource
ContextVars consistent across LangGraph nodes even though Starlette advances a
sync StreamingResponse generator across different threadpool threads.
"""
from __future__ import annotations

import queue
import threading
from collections.abc import Iterator
from typing import Any

from langchain_core.messages import AIMessage, AIMessageChunk, BaseMessage, HumanMessage, ToolMessage

from ..content.sink import new_sink
from ..tools.context import set_datasource_scope
from .streaming import block_events


def _iter_stream_chunks(graph, payload: dict, config: dict) -> Iterator[Any]:
    """Yield message chunks from the graph, tolerating tuple-or-object forms."""
    for item in graph.stream(payload, stream_mode="messages", config=config):
        if isinstance(item, tuple) and len(item) == 2:
            yield item[0]
        else:
            yield item


def _run_once(
    graph,
    user_text: str,
    datasource_ids: list[int] | None,
    history: list[BaseMessage] | None,
    recursion_limit: int,
    out: queue.Queue,
) -> None:
    set_datasource_scope(datasource_ids)
    new_sink()
    messages = list(history or []) + [HumanMessage(content=user_text)]
    try:
        for chunk in _iter_stream_chunks(
            graph,
            {"messages": messages},
            {"recursion_limit": recursion_limit},
        ):
            if isinstance(chunk, AIMessageChunk):
                for tc in (chunk.tool_call_chunks or []):
                    name = tc.get("name") if isinstance(tc, dict) else getattr(tc, "name", None)
                    if name:
                        out.put({"type": "tool_start", "name": name})
                if chunk.content:
                    out.put({"type": "token", "content": chunk.content})
            elif isinstance(chunk, AIMessage):
                for tc in (getattr(chunk, "tool_calls", None) or []):
                    name = tc.get("name") if isinstance(tc, dict) else ""
                    if name:
                        out.put({"type": "tool_start", "name": name})
                if chunk.content:
                    out.put({"type": "token", "content": chunk.content})
            elif isinstance(chunk, ToolMessage):
                out.put({
                    "type": "tool_end",
                    "name": getattr(chunk, "name", "") or "",
                    "content": str(chunk.content)[:800],
                })
                for ev in block_events():
                    out.put(ev)
        for ev in block_events():
            out.put(ev)
        out.put({"type": "done"})
    except Exception as e:  # noqa: BLE001
        for ev in block_events():
            out.put(ev)
        out.put({"type": "error", "content": f"{type(e).__name__}: {e}"})
    finally:
        out.put(None)  # sentinel: end of stream


def run_stream(
    graph,
    user_text: str,
    datasource_ids: list[int] | None,
    history: list[BaseMessage] | None = None,
    recursion_limit: int = 25,
) -> Iterator[dict[str, Any]]:
    """Run the agent in a dedicated thread; yield SSE-ready event dicts."""
    out: queue.Queue[dict[str, Any] | None] = queue.Queue()
    worker = threading.Thread(
        target=_run_once,
        args=(graph, user_text, datasource_ids, history, recursion_limit, out),
        daemon=True,
    )
    worker.start()
    while True:
        ev = out.get()
        if ev is None:
            break
        yield ev
    worker.join(timeout=1)
