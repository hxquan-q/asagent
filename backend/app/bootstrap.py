"""Startup bootstrap: create tables + seed the single admin user."""
from __future__ import annotations

from sqlmodel import Session, SQLModel, select

from .core.config import settings
from .core.db import get_engine
from .core.security import hash_password
from .models import User


def init_db() -> None:
    SQLModel.metadata.create_all(get_engine())


def seed_admin() -> None:
    with Session(get_engine()) as session:
        existing = session.exec(
            select(User).where(User.username == settings.ADMIN_USERNAME)
        ).first()
        if existing is None:
            session.add(
                User(
                    username=settings.ADMIN_USERNAME,
                    password_hash=hash_password(settings.ADMIN_PASSWORD),
                    is_admin=True,  # explicit: bootstrap admin only
                )
            )
            session.commit()
