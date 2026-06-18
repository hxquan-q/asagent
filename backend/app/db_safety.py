"""SQL read-only enforcement (defence in depth).

Order matters: parse to AST first, reject multi-statement stacking and any
non-SELECT root, then denylist dangerous functions on the **normalised**
(comment-stripped) SQL so comment/casing tricks cannot bypass the substring
check. (Borrowed from SQLBot ``apps/db/db.py`` + postgresai regex denylist.)
"""
from __future__ import annotations

import sqlglot
from sqlglot import exp
from sqlglot.errors import SqlglotError

# Substrings (lowercase) blocked inside an otherwise-valid SELECT.
_DENY_SUBSTRINGS = (
    "pg_read_file", "pg_read_binary_file", "pg_ls_dir", "pg_stat_file",
    "dblink", "lo_export", "lo_import", "pg_sleep",
    "copy ", "copy(", "to program", "pg_execute_server_program",
)


def assert_read_only(sql: str, dialect: str = "postgres") -> None:
    """Raise ``ValueError`` unless ``sql`` is a single read-only SELECT."""
    sql = (sql or "").strip()
    while sql.endswith(";"):
        sql = sql[:-1].strip()
    if not sql:
        raise ValueError("empty SQL")

    try:
        statements = sqlglot.parse(sql, read=dialect)
    except SqlglotError as e:
        raise ValueError(f"could not parse SQL: {e}") from e
    if not statements:
        raise ValueError("could not parse SQL")
    if len(statements) > 1:
        raise ValueError("multiple SQL statements are not allowed")

    stmt = statements[0]
    if not isinstance(stmt, (exp.Select, exp.With)):
        raise ValueError(
            f"only SELECT (optionally WITH ... SELECT) is allowed; got {type(stmt).__name__}"
        )

    # Normalised SQL drops comments, so comment-split tokens can't slip past.
    normalized = stmt.sql(dialect=dialect).lower()
    for bad in _DENY_SUBSTRINGS:
        if bad in normalized:
            raise ValueError(f"disallowed token in SQL: {bad.strip()}")
