"""Optional outbound HTTP tool.

SSRF-guarded: only http(s), private/loopback/non-routable hosts blocked, methods
restricted, and Authorization/Cookie headers stripped from the request. NOT in
the default tool set — enable per-agent only when the deployment trusts the model.
"""
from __future__ import annotations

import re

import httpx
from langchain_core.tools import tool

from ..core.net import assert_safe_url

_ALLOWED_METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE", "HEAD"}
_DROP_HEADERS = {"authorization", "cookie", "set-cookie"}
# Redact obvious secrets leaked in response bodies (defence-in-depth).
_SECRET_RE = re.compile(
    r"(?i)(api[_-]?key|access[_-]?token|auth[_-]?token|secret|password|passwd|authorization)"
    r"(\"|'||\s)?\s*[:=]\s*(\"|'|)?[^\"'&\s]{6,}"
)


def _redact(text: str) -> str:
    return _SECRET_RE.sub(r"\1\2\3***REDACTED***", text)


@tool
def http_request(method: str, url: str, headers: dict | None = None, body: str | None = None,
                 timeout: float = 15.0) -> str:
    """Perform an outbound HTTP request and return status + truncated body.

    Internal/private hosts are blocked; Authorization and Cookie headers are dropped.

    Args:
        method: GET | POST | PUT | PATCH | DELETE | HEAD.
        url: absolute http(s) URL (private hosts blocked).
        headers: optional request headers (Authorization/Cookie stripped).
        body: optional request body (string).
        timeout: seconds.
    """
    m = (method or "").upper()
    if m not in _ALLOWED_METHODS:
        raise ValueError(f"method not allowed: {method!r}; allowed: {sorted(_ALLOWED_METHODS)}")
    assert_safe_url(url)
    clean_headers = {k: v for k, v in (headers or {}).items() if k.lower() not in _DROP_HEADERS}

    with httpx.Client(timeout=timeout, follow_redirects=False) as client:
        resp = client.request(m, url, headers=clean_headers, content=body)
    text = _redact(resp.text)
    suffix = "…" if len(text) > 1500 else ""
    return f"HTTP {resp.status_code}\n{text[:1500]}{suffix}"


HTTP_TOOLS = [http_request]
