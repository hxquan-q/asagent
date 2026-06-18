"""Chart visualisation tool (ECharts).

The agent supplies a chart type and a valid ECharts option object; the tool emits
a ``ChartBlock`` to the client (rendered by ECharts) and returns a short note to
the agent. Deterministic rendering — the model provides data, not executable code.
"""
from __future__ import annotations

import json
from typing import Any

from langchain_core.tools import tool

from ..content.blocks import ChartBlock
from ..content.sink import emit_block

_CHART_TYPES = {
    "bar", "line", "pie", "scatter", "area", "radar", "heatmap",
    "funnel", "graph", "boxplot", "candlestick", "treemap", "sunburst",
    "sankey", "gauge", "map",
}
_MAX_SPEC_CHARS = 50_000


@tool
def visualize(chart_type: str, title: str, spec: dict[str, Any]) -> str:
    """Render a data chart for the user.

    Call this after querying data to visualise results.

    Args:
        chart_type: one of bar | line | pie | scatter | area | radar | heatmap | funnel | graph | boxplot | candlestick | treemap | sunburst | sankey | gauge | map.
        title: chart title (may be empty).
        spec: a valid ECharts `option` object (e.g. {"tooltip":{}, "xAxis":{"type":"category","data":[...]}, "yAxis":{"type":"value"}, "series":[{"name":..,"type":"bar","data":[...]}]}).
    """
    ct = (chart_type or "").strip().lower()
    if ct not in _CHART_TYPES:
        raise ValueError(f"unsupported chart_type: {chart_type!r}; allowed: {sorted(_CHART_TYPES)}")
    encoded = json.dumps(spec or {}, ensure_ascii=False)
    if len(encoded) > _MAX_SPEC_CHARS:
        raise ValueError(f"chart spec too large ({len(encoded)} chars; max {_MAX_SPEC_CHARS})")
    emit_block(ChartBlock(chart_type=ct, title=title, spec=spec or {}))
    return f"Chart rendered ({ct}): {title or 'untitled'}"


VISUALIZE_TOOLS = [visualize]
