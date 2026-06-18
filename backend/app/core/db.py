"""Metadata DB engine + session dependency (sync SQLAlchemy/SQLModel).

This engine talks to the platform's OWN Postgres (agents, datasources, llm
configs, skills registry, conversations, users, api keys). Business databases
(WMS etc.) are connected dynamically at runtime by ``app.datasources.manager``.
"""
from __future__ import annotations

from collections.abc import Generator

from sqlmodel import Session, create_engine

from .config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=settings.DEBUG,
)


def get_session() -> Generator[Session, None, None]:
    """FastAPI dependency yielding a scoped session."""
    with Session(engine) as session:
        yield session
