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

    # Metadata DB (platform's own Postgres). No shipped credentials — set via env.
    DATABASE_URL: str = ""
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
                data = json.loads(raw)
            except json.JSONDecodeError as e:
                raise ValueError(f"CORS_ORIGINS is not valid JSON: {e}") from e
            return [o.strip() for o in data if isinstance(o, str) and o.strip()]
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

    def validate_runtime_secrets(self) -> None:
        """Ensure shipped defaults aren't used in production.

        Call once at startup. In DEBUG we generate ephemeral random secrets
        (with a warning) so local dev works; in production we fail fast.

        Idempotent: safe to call from multiple entry points (lifespan, get_engine).
        """
        global _secrets_validated
        if _secrets_validated:
            return

        import logging
        import secrets as _secrets

        log = logging.getLogger("asagent")
        weak = [
            name for name in ("SECRET_KEY", "JWT_SECRET")
            if getattr(self, name).startswith("change-me")
        ]
        if weak:
            if self.DEBUG:
                for name in weak:
                    setattr(self, name, _secrets.token_urlsafe(48))
                log.warning(
                    "Generated ephemeral %s (DEBUG only). Set them in .env for production.",
                    weak,
                )
            else:
                raise RuntimeError(
                    f"Refusing to start: default secrets in use: {weak}. "
                    "Set SECRET_KEY/JWT_SECRET via environment."
                )
        if len(self.JWT_SECRET.encode("utf-8")) < 32:
            if self.DEBUG:
                self.JWT_SECRET = _secrets.token_urlsafe(32)
                log.warning("JWT_SECRET too short; generated ephemeral (DEBUG only).")
            else:
                raise RuntimeError("JWT_SECRET must be >= 32 bytes for HS256.")
        if self.ADMIN_PASSWORD == "admin123":
            log.warning(
                "ADMIN_PASSWORD is the shipped default 'admin123' — set ADMIN_PASSWORD "
                "in .env for any non-local deployment."
            )
        if not self.DATABASE_URL:
            if self.DEBUG:
                self.DATABASE_URL = "sqlite:///./data/asagent.db"
                log.warning("DATABASE_URL not set; using local sqlite (DEBUG only).")
            else:
                raise RuntimeError("DATABASE_URL must be set via environment.")

        _secrets_validated = True  # noqa: PLW0603 — intentional module-level success flag


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

# Guard for idempotent startup secret validation.
_secrets_validated = False


@lru_cache(maxsize=1)
def _get_fernet() -> Fernet:
    # Derive a valid 32-byte Fernet key from SECRET_KEY so any string works
    # (no need for the operator to generate a Fernet-formatted key).
    key = base64.urlsafe_b64encode(hashlib.sha256(settings.SECRET_KEY.encode("utf-8")).digest())
    return Fernet(key)
