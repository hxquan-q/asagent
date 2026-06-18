from __future__ import annotations

import pytest

from app.db_safety import assert_read_only


def test_allows_select_and_cte():
    assert_read_only("SELECT 1")
    assert_read_only("WITH t AS (SELECT 1) SELECT * FROM t")
    assert_read_only("select a, b from t where x = 1 order by a")
    assert_read_only("SELECT * FROM t /* a comment */ LIMIT 10")


@pytest.mark.parametrize(
    "sql",
    [
        "INSERT INTO t VALUES (1)",
        "UPDATE t SET x = 1",
        "DELETE FROM t",
        "DROP TABLE t",
        "CREATE TABLE t (x int)",
        "TRUNCATE t",
        "SELECT pg_read_file('x')",
        "SELECT * FROM dblink('x', 'y')",
        "SELECT 1; DROP TABLE t",            # statement stacking
        "COPY t TO PROGRAM 'rm -rf /'",      # command exec
        "SELECT pg_read_file /* x */ ('a')", # comment-wrapped dangerous fn
    ],
)
def test_rejects_dangerous(sql):
    with pytest.raises(ValueError):
        assert_read_only(sql)
