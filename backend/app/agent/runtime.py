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
import time
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
    stall_timeout: float = 180.0,
    poll_interval: float = 5.0,
) -> Iterator[dict[str, Any]]:
    """Run the agent in a dedicated thread; yield SSE-ready event dicts.

    A watchdog bounds stalls: if no event arrives for ``stall_timeout`` seconds
    (e.g. a hung LLM/tool call), an ``error`` event is emitted and the stream
    ends so the client connection and queue reader are never blocked forever.
    The daemon worker is reaped once the underlying call finishes (it is also
    bounded by the model's request timeout).
    """
    out: queue.Queue[dict[str, Any] | None] = queue.Queue()
    worker = threading.Thread(
        target=_run_once,
        args=(graph, user_text, datasource_ids, history, recursion_limit, out),
        daemon=True,
    )
    worker.start()
    last_activity = time.monotonic()
    while True:
        try:
            ev = out.get(timeout=poll_interval)
        except queue.Empty:
            if not worker.is_alive():
                yield {"type": "error", "content": "agent worker terminated unexpectedly"}
                break
            if time.monotonic() - last_activity > stall_timeout:
                yield {"type": "error", "content": f"agent stalled (no output for {stall_timeout:.0f}s)"}
                break
            continue
        last_activity = time.monotonic()
        if ev is None:
            break
        yield ev
    worker.join(timeout=1)
