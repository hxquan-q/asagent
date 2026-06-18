"""URL / SSRF guards for outbound tools (http_request, make_image)."""
from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urlparse

_ALLOWED_SCHEMES = {"http", "https"}


def assert_safe_url(url: str, allow_data: bool = False) -> None:
    """Reject non-http(s) schemes and private/loopback/non-routable hosts.

    Note: a determined attacker can still race DNS rebinding between the resolve
    and the actual request; treat this as defence-in-depth, not a complete
    sandbox. Network egress controls belong at the infrastructure layer too.
    """
    parsed = urlparse(url)
    scheme = (parsed.scheme or "").lower()
    if scheme == "data" and allow_data:
        return
    if scheme not in _ALLOWED_SCHEMES:
        raise ValueError(f"URL scheme not allowed: {scheme or '(none)'}")

    host = parsed.hostname or ""
    if not host:
        raise ValueError("URL has no host")

    try:
        infos = socket.getaddrinfo(host, None)
    except socket.gaierror as e:
        raise ValueError(f"cannot resolve host {host!r}: {e}") from e

    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if (
            ip.is_private or ip.is_loopback or ip.is_link_local
            or ip.is_reserved or ip.is_multicast or ip.is_unspecified
        ):
            raise ValueError(f"internal/non-routable host blocked: {host}")
