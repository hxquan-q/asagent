"""Built-in agent tools."""
from .http_request import HTTP_TOOLS, http_request
from .query_database import QUERY_TOOLS, describe_schema, query_database
from .render import RENDER_TOOLS, make_diagram, make_html, make_image, make_svg, save_file
from .visualize import VISUALIZE_TOOLS, visualize

# Default toolkit every agent gets unless its config restricts it.
DEFAULT_TOOLS = [*QUERY_TOOLS, *VISUALIZE_TOOLS, *RENDER_TOOLS]

__all__ = [
    "QUERY_TOOLS", "VISUALIZE_TOOLS", "RENDER_TOOLS", "HTTP_TOOLS",
    "DEFAULT_TOOLS",
    "describe_schema", "query_database", "visualize",
    "make_diagram", "make_svg", "make_html", "make_image", "save_file", "http_request",
]
