"""Dynamic business-datasource engines (Postgres) + read execution.

Each configured Datasource (e.g. a WMS database) gets a pooled SQLAlchemy engine
cached by id. Engines talk to the BUSINESS database in read-only fashion (SQL is
validated by :mod:`app.db_safety` before execution).
"""
from __future__ import annotations

from typing import Any

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from ..core.config import settings
from ..db_safety import assert_read_only

_engines: dict[int, Engine] = {}


def _dialect_for(type_: str) -> str:
    return "postgres" if type_ in ("postgres", "postgresql") else type_


def get_datasource_engine(row) -> Engine:
    """Return a cached engine for a Datasource ORM row (decrypts password)."""
    eng = _engines.get(row.id)
    if eng is None:
        password = settings.decrypt(row.password_encrypted)
        eng = create_engine(
            row.dsn(password),
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
            pool_recycle=3600,
        )
        _engines[row.id] = eng
    return eng


def drop_datasource_engine(datasource_id: int) -> None:
    _engines.pop(datasource_id, None)


def execute_read_on_engine(
    engine: Engine, sql: str, dialect: str = "postgres", max_rows: int = 200
) -> tuple[list[str], list[dict[str, Any]]]:
    """Validate + execute a read query on an engine; return (columns, rows)."""
    assert_read_only(sql, dialect=dialect)
    with engine.connect() as conn:
        result = conn.execute(text(sql))
        columns = list(result.keys())
        rows = [dict(zip(columns, row)) for row in result.fetchmany(max_rows)]
    return columns, rows


def execute_read(row, sql: str, max_rows: int = 200) -> tuple[list[str], list[dict[str, Any]]]:
    engine = get_datasource_engine(row)
    return execute_read_on_engine(engine, sql, dialect=_dialect_for(row.type), max_rows=max_rows)
