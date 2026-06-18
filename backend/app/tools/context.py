"""Per-invocation agent context (authorization scopes).

The runtime sets the active agent's datasource scope before invoking the model;
the query tools consult it so an agent can only touch datasources it was bound
to (``Agent.datasource_ids``). ``None`` means unrestricted (admin/console).
"""
from __future__ import annotations

from contextvars import ContextVar

_datasource_scope: ContextVar[list[int] | None] = ContextVar("datasource_scope", default=None)


def set_datasource_scope(ids: list[int] | None) -> None:
    _datasource_scope.set(list(ids) if ids is not None else None)


def get_datasource_scope() -> list[int] | None:
    return _datasource_scope.get()


def datasource_allowed(datasource_id: int) -> bool:
    scope = _datasource_scope.get()
    return scope is None or datasource_id in scope
