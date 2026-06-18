"""Rich-render tools: diagrams (Mermaid), SVG, HTML, images, files.

Each tool emits a typed content block to the client and returns a short note to
the agent. HTML/SVG are sanitised server-side (nh3) on block construction.
"""
from __future__ import annotations

import re
import uuid

from langchain_core.tools import tool

from ..content.blocks import DiagramBlock, FileBlock, HtmlBlock, ImageBlock, SvgBlock
from ..content.sink import emit_block
from ..core.config import settings
from ..core.net import assert_safe_url

_FILE_MIME_ALLOWLIST = {
    "text/plain", "text/csv", "text/markdown", "text/html",
    "application/json", "text/tab-separated-values", "application/xml",
    "image/svg+xml",
}
_MAX_FILE_BYTES = 10 * 1024 * 1024  # 10 MB
_MAX_DATA_URL = 2 * 1024 * 1024     # 2 MB inline data: URL


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
    """Show an image. ``url`` may be an http(s) URL or a data: URL (private hosts blocked)."""
    assert_safe_url(url, allow_data=True)
    if url.startswith("data:") and len(url) > _MAX_DATA_URL:
        raise ValueError(f"data: URL too large ({len(url)} bytes; max {_MAX_DATA_URL})")
    emit_block(ImageBlock(url=url, alt=alt, title=title))
    return f"Image rendered: {alt or title or url[:40]}"


@tool
def save_file(filename: str, content: str, mime: str = "text/plain") -> str:
    """Save text content as a downloadable file and surface it to the user.

    Args:
        filename: suggested filename, e.g. "report.csv".
        content: the file's text content (<= 10 MB).
        mime: one of text/csv, application/json, text/plain, text/html, ...
    """
    if mime not in _FILE_MIME_ALLOWLIST:
        raise ValueError(f"mime not allowed: {mime!r}; allowed: {sorted(_FILE_MIME_ALLOWLIST)}")
    if len(content) > _MAX_FILE_BYTES:
        raise ValueError(f"content too large ({len(content)} bytes; max {_MAX_FILE_BYTES})")

    safe_name = re.sub(r"[^A-Za-z0-9._-]", "_", filename or "")[:128] or "file"
    stored = f"{uuid.uuid4().hex}_{safe_name}"
    settings.ensure_dirs()
    path = settings.files_path / stored
    path.write_text(content, encoding="utf-8")
    emit_block(
        FileBlock(
            filename=safe_name,
            mime=mime,
            url=f"/api/v1/files/{stored}",
            size=path.stat().st_size,
        )
    )
    return f"File saved: {safe_name} ({path.stat().st_size} bytes)"


RENDER_TOOLS = [make_diagram, make_svg, make_html, make_image, save_file]
