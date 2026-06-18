"""Datasource subsystem: dynamic business-DB engines + schema introspection."""
from .introspect import describe, describe_from_engine, schema_summary, schema_summary_from_engine
from .manager import drop_datasource_engine, execute_read, execute_read_on_engine, get_datasource_engine

__all__ = [
    "get_datasource_engine", "drop_datasource_engine",
    "execute_read", "execute_read_on_engine",
    "describe", "describe_from_engine", "schema_summary", "schema_summary_from_engine",
]
