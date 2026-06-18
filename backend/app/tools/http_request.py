"""Optional outbound HTTP tool.

WARNING: SSRF surface — lets the agent call arbitrary URLs. NOT in the default
tool set; enable per-agent only when the deployment trusts the model and the
network egress is controlled. Consider adding an allowlist for production.
"""
from __future__ import annotations

import httpx
from langchain_core.tools import tool


@tool
def http_request(method: str, url: str, headers: dict | None = None, body: str | None = None,
                 timeout: float = 15.0) -> str:
    """Perform an outbound HTTP request and return status + truncated body.

    Args:
        method: GET | POST | PUT | DELETE.
        url: absolute URL.
        headers: optional request headers.
        body: optional request body (string).
        timeout: seconds.
    """
    with httpx.Client(timeout=timeout) as client:
        resp = client.request(method, url, headers=headers or {}, content=body)
    text = resp.text
    return f"HTTP {resp.status_code}\n{(text[:1500])}{'…' if len(text) > 1500 else ''}"


HTTP_TOOLS = [http_request]
