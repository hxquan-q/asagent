"""SQLModel ORM tables (platform metadata DB).

All secrets (LLM api keys, datasource passwords) are stored encrypted; their
columns end with ``_encrypted`` and are produced by ``settings.encrypt``.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import JSON, Column, DateTime, Text
from sqlmodel import Field, SQLModel


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True, max_length=64)
    password_hash: str = Field(max_length=255)
    is_admin: bool = Field(default=True)
    created_at: datetime = Field(default_factory=now_utc)


class ApiKey(SQLModel, table=True):
    __tablename__ = "api_keys"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=128)
    key_prefix: str = Field(index=True, max_length=16)  # first chars of plaintext, for lookup
    key_hash: str = Field(index=True, max_length=128)   # sha256 of full plaintext key
    created_by: Optional[int] = Field(default=None, foreign_key="users.id")
    last_used_at: Optional[datetime] = Field(default=None)
    enabled: bool = Field(default=True)
    expires_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=now_utc)


class LlmConfig(SQLModel, table=True):
    __tablename__ = "llm_configs"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True, max_length=128)
    provider: str = Field(max_length=32)  # openai | tongyi | deepseek | ollama | custom
    model_name: str = Field(max_length=128)
    api_base_url: str = Field(default="", max_length=512)
    api_key_encrypted: str = Field(default="", max_length=2048)
    additional_params: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    is_default: bool = Field(default=False)
    enabled: bool = Field(default=True)
    created_at: datetime = Field(default_factory=now_utc)


class Datasource(SQLModel, table=True):
    __tablename__ = "datasources"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True, max_length=128)
    type: str = Field(default="postgres", max_length=32)
    host: str = Field(max_length=256)
    port: int = Field(default=5432)
    db: str = Field(max_length=128)
    username: str = Field(max_length=128)
    password_encrypted: str = Field(default="", max_length=2048)
    options: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    enabled: bool = Field(default=True)
    created_at: datetime = Field(default_factory=now_utc)

    def dsn(self, decrypted_password: str) -> str:
        """Build a SQLAlchemy URL with a decrypted password."""
        from urllib.parse import quote_plus

        pwd = quote_plus(decrypted_password) if decrypted_password else ""
        auth = f"{quote_plus(self.username)}:{pwd}" if pwd else quote_plus(self.username)
        return f"postgresql+psycopg://{auth}@{self.host}:{self.port}/{self.db}"


class Agent(SQLModel, table=True):
    __tablename__ = "agents"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, max_length=128)
    description: str = Field(default="", max_length=512)
    system_prompt: str = Field(default="", sa_column=Column(Text))
    llm_config_id: Optional[int] = Field(default=None, foreign_key="llm_configs.id")
    datasource_ids: list[int] = Field(default_factory=list, sa_column=Column(JSON))
    tool_set: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    skill_ids: list[int] = Field(default_factory=list, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=now_utc)
    updated_at: datetime = Field(default_factory=now_utc)


class Skill(SQLModel, table=True):
    __tablename__ = "skills"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True, max_length=64)
    description: str = Field(default="", sa_column=Column(Text))
    dir_path: str = Field(max_length=512)
    version: str = Field(default="1.0.0", max_length=32)
    license: str = Field(default="", max_length=128)
    compatibility: str = Field(default="", sa_column=Column(Text))
    skill_metadata: dict[str, Any] = Field(
        default_factory=dict, sa_column=Column("metadata", JSON)
    )
    allowed_tools: str = Field(default="", max_length=512)
    enabled: bool = Field(default=True)
    uploaded_by: Optional[int] = Field(default=None, foreign_key="users.id")
    uploaded_at: datetime = Field(default_factory=now_utc)
    updated_at: datetime = Field(default_factory=now_utc)


class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: Optional[int] = Field(default=None, primary_key=True)
    agent_id: Optional[int] = Field(default=None, foreign_key="agents.id")
    api_key_id: Optional[int] = Field(default=None, foreign_key="api_keys.id")
    title: str = Field(default="New conversation", max_length=256)
    created_at: datetime = Field(default_factory=now_utc)


class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: Optional[int] = Field(default=None, foreign_key="conversations.id", index=True)
    role: str = Field(max_length=16)  # user | assistant | tool
    blocks: list[dict[str, Any]] = Field(default_factory=list, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=now_utc)


__all__ = [
    "User", "ApiKey", "LlmConfig", "Datasource", "Agent", "Skill",
    "Conversation", "Message",
]
