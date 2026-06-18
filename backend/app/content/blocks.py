"""Multi-format content blocks.

The agent emits a sequence of typed blocks instead of plain text. Both the API
(JSON / SSE) and the frontend render understand these types. Skills can dictate
which block type the agent should produce via SKILL.md instructions.
"""
from __future__ import annotations

from typing import Any, Literal, Union

from pydantic import BaseModel, Field


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
    content: str = ""


class HtmlBlock(BaseModel):
    type: Literal["html"] = "html"
    title: str = ""
    content: str = ""  # sanitised client-side with DOMPurify + sandboxed iframe


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
