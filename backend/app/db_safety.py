"""SQL read-only enforcement (defence in depth).

Two layers (borrowed from SQLBot ``apps/db/db.py`` + postgresai regex denylist):
1. statement-type filter via sqlglot — only ``SELECT`` (with optional CTE) allowed
2. substring denylist for dangerous tokens embedded inside a SELECT
   (``pg_read_file``, ``dblink``, ``COPY ... TO PROGRAM``, ...)
"""
from __future__ import annotations

import sqlglot
from sqlglot import exp

# Substrings (lowercase) blocked even inside a SELECT.
_DENY_SUBSTRINGS = (
    "pg_read_file", "pg_read_binary_file", "pg_ls_dir", "pg_stat_file",
    "dblink", "lo_export", "lo_import", "pg_sleep",
    "copy ", "copy(", "to program", "pg_execute_server_program",
    "create ", "insert ", "update ", "delete ", "drop ", "alter ",
    "truncate ", "grant ", "revoke ", "vacuum",
)


def assert_read_only(sql: str, dialect: str = "postgres") -> None:
    """Raise ``ValueError`` if ``sql`` is anything other than a read query."""
    sql = (sql or "").strip()
    if sql.endswith(";"):
        sql = sql[:-1].strip()
    if not sql:
        raise ValueError("empty SQL")

    lowered = sql.lower()
    for bad in _DENY_SUBSTRINGS:
        if bad in lowered:
            raise ValueError(f"disallowed token in SQL: {bad.strip()}")

    statements = sqlglot.parse(sql, read=dialect)
    if not statements:
        raise ValueError("could not parse SQL")

    for stmt in statements:
        if not isinstance(stmt, (exp.Select, exp.With)):
            raise ValueError(
                f"only SELECT (optionally WITH ... SELECT) is allowed; got {type(stmt).__name__}"
            )
