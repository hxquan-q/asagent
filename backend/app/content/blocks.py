"""Multi-format content blocks.

The agent emits a sequence of typed blocks instead of plain text. Both the API
(JSON / SSE) and the frontend render understand these types. Skills can dictate
which block type the agent should produce via SKILL.md instructions.
"""
from __future__ import annotations

from typing import Any, Literal, Union

import nh3
from pydantic import BaseModel, Field, field_validator


# ---- server-side HTML/SVG sanitisation (defence in depth; client also runs DOMPurify) ----
_HTML_TAGS = {
    "a", "abbr", "b", "blockquote", "br", "code", "dd", "del", "div", "dl", "dt", "em",
    "h1", "h2", "h3", "h4", "h5", "h6", "hr", "i", "img", "ins", "kbd", "li", "ol", "p",
    "pre", "q", "s", "samp", "small", "span", "strong", "sub", "sup", "table", "tbody",
    "td", "tfoot", "th", "thead", "tr", "u", "ul", "var", "details", "summary",
}
_HTML_ATTRS = {
    "*": {"class", "style", "title", "id", "colspan", "rowspan", "width", "height", "align", "valign"},
    "a": {"href", "title", "name", "target"},
    "img": {"src", "alt", "width", "height"},
}
_SVG_TAGS = {
    "svg", "g", "defs", "symbol", "use", "title", "desc", "path", "rect", "circle",
    "ellipse", "line", "polyline", "polygon", "text", "tspan", "linearGradient",
    "radialGradient", "stop", "pattern", "clipPath", "mask",
}
_SVG_ATTRS = {
    "*": {"id", "class", "style", "transform", "viewBox", "preserveAspectRatio", "xmlns",
          "x", "y", "x1", "y1", "x2", "y2", "cx", "cy", "r", "rx", "ry", "width", "height",
          "fill", "fill-opacity", "stroke", "stroke-width", "stroke-opacity", "opacity",
          "d", "points", "font-size", "font-family", "text-anchor", "offset", "stop-color",
          "stop-opacity", "gradientTransform", "gradientUnits", "href", "xlink:href"},
}


def _sanitize_html(s: str) -> str:
    if not s:
        return ""
    return nh3.clean(
        s, tags=_HTML_TAGS, attributes=_HTML_ATTRS,
        clean_content_tags={"script", "style"}, strip_comments=True,
    )


def _sanitize_svg(s: str) -> str:
    if not s:
        return ""
    return nh3.clean(
        s, tags=_SVG_TAGS, attributes=_SVG_ATTRS,
        clean_content_tags={"script"}, strip_comments=True,
    )


class TextBlock(BaseModel):
    type: Literal["text"] = "text"
    content: str = ""


class TableColumn(BaseModel):
    name: str
    type: str = "string"


class TableBlock(BaseModel):
    type: Literal["table"] = "table"
    title: str = ""
    columns: list[TableColumn] = Field(default_factory=list)
    rows: list[dict[str, Any]] = Field(default_factory=list)


class ChartBlock(BaseModel):
    type: Literal["chart"] = "chart"
    title: str = ""
    chart_type: str = "bar"  # bar | line | pie | scatter | ...
    spec: dict[str, Any] = Field(default_factory=dict)  # ECharts option object


class DiagramBlock(BaseModel):
    type: Literal["diagram"] = "diagram"
    engine: Literal["mermaid"] = "mermaid"
    title: str = ""
    source: str = ""


class SvgBlock(BaseModel):
    type: Literal["svg"] = "svg"
    title: str = ""
    content: str = ""  # server-sanitised (nh3): scripts / event handlers stripped

    @field_validator("content", mode="after")
    @classmethod
    def _clean_svg(cls, v: str) -> str:
        return _sanitize_svg(v)


class HtmlBlock(BaseModel):
    type: Literal["html"] = "html"
    title: str = ""
    content: str = ""  # server-sanitised (nh3) + client DOMPurify + sandboxed iframe

    @field_validator("content", mode="after")
    @classmethod
    def _clean_html(cls, v: str) -> str:
        return _sanitize_html(v)


class ImageBlock(BaseModel):
    type: Literal["image"] = "image"
    title: str = ""
    url: str = ""  # http(s) URL or data: URL
    alt: str = ""


class FileBlock(BaseModel):
    type: Literal["file"] = "file"
    filename: str = ""
    mime: str = "application/octet-stream"
    url: str = ""
    size: int = 0


class DataBlock(BaseModel):
    type: Literal["data"] = "data"
    mime: str = "application/json"
    content: Any = None


Block = Union[
    TextBlock, TableBlock, ChartBlock, DiagramBlock,
    SvgBlock, HtmlBlock, ImageBlock, FileBlock, DataBlock,
]

_BLOCK_CLASSES = {
    "text": TextBlock, "table": TableBlock, "chart": ChartBlock,
    "diagram": DiagramBlock, "svg": SvgBlock, "html": HtmlBlock,
    "image": ImageBlock, "file": FileBlock, "data": DataBlock,
}


def block_to_dict(block: BaseModel) -> dict[str, Any]:
    return block.model_dump()


def dict_to_block(data: dict[str, Any]) -> BaseModel:
    cls = _BLOCK_CLASSES.get(data.get("type", "text"), TextBlock)
    return cls.model_validate(data)


__all__ = [
    "TextBlock", "TableColumn", "TableBlock", "ChartBlock", "DiagramBlock",
    "SvgBlock", "HtmlBlock", "ImageBlock", "FileBlock", "DataBlock",
    "Block", "block_to_dict", "dict_to_block",
]
