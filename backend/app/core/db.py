"""Metadata DB engine + session dependency (sync SQLAlchemy/SQLModel).

Engine is created lazily so startup secret validation (which may resolve
``DATABASE_URL``) runs first. This engine talks to the platform's OWN database;
business databases (WMS etc.) are connected dynamically by
``app.datasources.manager``.
"""
from __future__ import annotations

from collections.abc import Generator
from functools import lru_cache

from sqlmodel import Session, create_engine

from .config import settings


@lru_cache(maxsize=1)
def get_engine():
    # Idempotent: ensures DATABASE_URL + secrets are resolved/validated before
    # the engine is created, regardless of the entry point.
    settings.validate_runtime_secrets()
    kwargs: dict = {"pool_pre_ping": True, "pool_recycle": 3600, "echo": settings.DEBUG}
    # pool_size / max_overflow belong to QueuePool (Postgres etc.), not SQLite.
    if not settings.DATABASE_URL.startswith("sqlite"):
        kwargs["pool_size"] = settings.DB_POOL_SIZE
        kwargs["max_overflow"] = settings.DB_MAX_OVERFLOW
    return create_engine(settings.DATABASE_URL, **kwargs)


def get_session() -> Generator[Session, None, None]:
    """FastAPI dependency yielding a scoped session."""
    with Session(get_engine()) as session:
        yield session
