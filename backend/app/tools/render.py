"""Rich-render tools: diagrams (Mermaid), SVG, HTML, images, files.

Each tool emits a typed content block to the client and returns a short note to
the agent. HTML/SVG are sanitised server-side (nh3) on block construction.
"""
from __future__ import annotations

import uuid
from typing import Any

from langchain_core.tools import tool

from ..content.blocks import DiagramBlock, FileBlock, HtmlBlock, ImageBlock, SvgBlock
from ..content.sink import emit_block
from ..core.config import settings


@tool
def make_diagram(source: str, title: str = "") -> str:
    """Render an architecture / flowchart / sequence diagram from Mermaid source.

    Args:
        source: valid Mermaid text (e.g. "graph TD; A-->B").
        title: optional diagram title.
    """
    emit_block(DiagramBlock(source=source, title=title))
    return f"Diagram rendered: {title or 'untitled'}"


@tool
def make_svg(svg: str, title: str = "") -> str:
    """Render an inline SVG for the user. Scripts/event handlers are stripped."""
    emit_block(SvgBlock(content=svg, title=title))
    return f"SVG rendered: {title or 'untitled'}"


@tool
def make_html(html: str, title: str = "") -> str:
    """Render a sanitised HTML fragment for the user (no <script>/event handlers)."""
    emit_block(HtmlBlock(content=html, title=title))
    return f"HTML rendered: {title or 'untitled'}"


@tool
def make_image(url: str, alt: str = "", title: str = "") -> str:
    """Show an image. ``url`` may be an http(s) URL or a data: URL."""
    emit_block(ImageBlock(url=url, alt=alt, title=title))
    return f"Image rendered: {alt or title or url[:40]}"


@tool
def save_file(filename: str, content: str, mime: str = "text/plain") -> str:
    """Save text content as a downloadable file and surface it to the user.

    Args:
        filename: suggested filename, e.g. "report.csv".
        content: the file's text content.
        mime: MIME type, e.g. "text/csv".
    """
    settings.ensure_dirs()
    safe_name = f"{uuid.uuid4().hex}_{filename}"
    path = settings.files_path / safe_name
    path.write_text(content, encoding="utf-8")
    emit_block(
        FileBlock(
            filename=filename,
            mime=mime,
            url=f"/api/v1/files/{safe_name}",
            size=path.stat().st_size,
        )
    )
    return f"File saved: {filename} ({path.stat().st_size} bytes)"


RENDER_TOOLS = [make_diagram, make_svg, make_html, make_image, save_file]
