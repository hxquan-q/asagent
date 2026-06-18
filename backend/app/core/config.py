"""Application settings (pydantic-settings).

Single source of truth for all configuration. Secrets that must be encrypted at
rest (LLM api keys, datasource passwords) are encrypted with the Fernet key in
``SECRET_KEY``; JWTs are signed with ``JWT_SECRET``.
"""
from __future__ import annotations

import base64
import hashlib
import json
from functools import lru_cache
from pathlib import Path

from cryptography.fernet import Fernet
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # App
    APP_NAME: str = "asagent"
    DEBUG: bool = False

    # Metadata DB (platform's own Postgres)
    DATABASE_URL: str = "postgresql+psycopg://asagent:asagent@localhost:5432/asagent"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20

    # Secrets
    SECRET_KEY: str = "change-me-generate-a-fernet-key"
    JWT_SECRET: str = "change-me-a-long-random-string"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days

    # Bootstrap admin
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin123"

    # API keys
    API_KEY_PREFIX: str = "ask"

    # Storage
    SKILLS_DIR: str = "./data/skills"
    FILES_DIR: str = "./data/files"

    # Sandbox
    SANDBOX_BACKEND: str = "pyodide"  # pyodide | docker
    SANDBOX_DOCKER_IMAGE: str = "asagent-sandbox:latest"
    SANDBOX_TIMEOUT_SECONDS: int = 30

    # CORS: comma-separated list or a JSON array string
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:8080"

    # ---- derived helpers ----
    @property
    def cors_origins(self) -> list[str]:
        raw = self.CORS_ORIGINS.strip()
        if raw.startswith("["):
            try:
                return [o.strip() for o in json.loads(raw) if o.strip()]
            except json.JSONDecodeError:
                pass
        return [o.strip() for o in raw.split(",") if o.strip()]

    @property
    def skills_path(self) -> Path:
        return Path(self.SKILLS_DIR).resolve()

    @property
    def files_path(self) -> Path:
        return Path(self.FILES_DIR).resolve()

    def ensure_dirs(self) -> None:
        self.skills_path.mkdir(parents=True, exist_ok=True)
        self.files_path.mkdir(parents=True, exist_ok=True)

    def encrypt(self, plaintext: str) -> str:
        """Encrypt a secret string for storage. Empty input stays empty."""
        if not plaintext:
            return ""
        return _get_fernet().encrypt(plaintext.encode()).decode()

    def decrypt(self, token: str) -> str:
        """Decrypt a stored secret. Empty/None stays empty."""
        if not token:
            return ""
        return _get_fernet().decrypt(token.encode()).decode()


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()


@lru_cache(maxsize=1)
def _get_fernet() -> Fernet:
    # Derive a valid 32-byte Fernet key from SECRET_KEY so any string works
    # (no need for the operator to generate a Fernet-formatted key).
    key = base64.urlsafe_b64encode(hashlib.sha256(settings.SECRET_KEY.encode("utf-8")).digest())
    return Fernet(key)
