"""Schema introspection for NL2SQL context (dialect-agnostic via SQLAlchemy)."""
from __future__ import annotations

from typing import Any

from sqlalchemy import inspect
from sqlalchemy.engine import Engine


def describe_from_engine(engine: Engine, max_tables: int = 200) -> dict[str, list[dict[str, str]]]:
    insp = inspect(engine)
    out: dict[str, list[dict[str, str]]] = {}
    for table in insp.get_table_names()[:max_tables]:
        out[table] = [
            {"name": col["name"], "type": str(col["type"])}
            for col in insp.get_columns(table)
        ]
    return out


def schema_summary_from_engine(engine: Engine, max_tables: int = 60) -> str:
    """Human-readable schema for the agent prompt."""
    schema = describe_from_engine(engine, max_tables=max_tables)
    if not schema:
        return "(no tables found)"
    lines = []
    for table, cols in schema.items():
        col_defs = ", ".join(f"{c['name']} {c['type']}" for c in cols)
        lines.append(f"TABLE {table} ({col_defs})")
    return "\n".join(lines)


def describe(row, **kwargs: Any) -> dict[str, list[dict[str, str]]]:
    from .manager import get_datasource_engine
    return describe_from_engine(get_datasource_engine(row), **kwargs)


def schema_summary(row, **kwargs: Any) -> str:
    from .manager import get_datasource_engine
    return schema_summary_from_engine(get_datasource_engine(row), **kwargs)
