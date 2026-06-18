"""Built-in NL2SQL tools exposed to agents.

Two-step ReAct pattern: the agent first inspects the schema, then writes and
runs a read-only SELECT. ``query_database`` emits a ``TableBlock`` to the client
(via the block sink) while returning a condensed textual preview to the agent.
"""
from __future__ import annotations

import json
from typing import Any

from langchain_core.tools import tool
from sqlmodel import Session, select

from ..content.blocks import TableBlock
from ..content.sink import emit_block
from ..core.db import get_engine
from ..datasources import manager
from ..models import Datasource


def _lookup_datasource(session: Session, name_or_id: str) -> Datasource:
    """Resolve an enabled datasource by id (int) or name."""
    try:
        ds_id = int(name_or_id)
        stmt = select(Datasource).where(Datasource.id == ds_id, Datasource.enabled == True)  # noqa: E712
    except ValueError:
        stmt = select(Datasource).where(Datasource.name == name_or_id, Datasource.enabled == True)  # noqa: E712
    ds = session.exec(stmt).first()
    if ds is None:
        raise ValueError(f"datasource '{name_or_id}' not found or disabled")
    return ds


@tool
def describe_schema(datasource_name: str) -> str:
    """Return the schema (tables + columns) of the given enabled datasource.

    Use this before writing SQL. Pass the datasource name or id.
    """
    from ..datasources import introspect

    with Session(get_engine()) as session:
        ds = _lookup_datasource(session, datasource_name)
        return introspect.schema_summary_from_engine(manager.get_datasource_engine(ds))


@tool
def query_database(datasource_name: str, sql: str) -> str:
    """Run a READ-ONLY SQL statement (SELECT / WITH ... SELECT) on a datasource.

    Args:
        datasource_name: name or id of an enabled datasource.
        sql: a single read-only SELECT query.

    Returns a textual row preview; a full table is rendered to the user.
    """
    with Session(get_engine()) as session:
        ds = _lookup_datasource(session, datasource_name)
        columns, rows = manager.execute_read(ds, sql)

    emit_block(
        TableBlock(
            columns=[{"name": c, "type": "auto"} for c in columns],
            rows=rows,
        )
    )
    preview = rows[:20]
    blob = json.dumps(preview, default=str, ensure_ascii=False)
    return (
        f"Returned {len(rows)} row(s). Columns: {columns}. "
        f"Preview (max 20 rows): {blob[:2000]}"
    )


QUERY_TOOLS = [describe_schema, query_database]

__all__ = ["describe_schema", "query_database", "QUERY_TOOLS"]
