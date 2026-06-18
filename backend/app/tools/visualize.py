"""Chart visualisation tool (ECharts).

The agent supplies a chart type and a valid ECharts option object; the tool emits
a ``ChartBlock`` to the client (rendered by ECharts) and returns a short note to
the agent. Deterministic rendering — the model provides data, not executable code.
"""
from __future__ import annotations

from typing import Any

from langchain_core.tools import tool

from ..content.blocks import ChartBlock
from ..content.sink import emit_block


@tool
def visualize(chart_type: str, title: str, spec: dict[str, Any]) -> str:
    """Render a data chart for the user.

    Call this after querying data to visualise results.

    Args:
        chart_type: one of bar | line | pie | scatter | area | ...
        title: chart title (may be empty).
        spec: a valid ECharts `option` object (e.g. {"tooltip":{}, "xAxis":{"type":"category","data":[...]}, "yAxis":{"type":"value"}, "series":[{"name":..,"type":"bar","data":[...]}]}).
    """
    emit_block(ChartBlock(chart_type=chart_type, title=title, spec=spec))
    return f"Chart rendered ({chart_type}): {title or 'untitled'}"


VISUALIZE_TOOLS = [visualize]
