"""Multi-vendor LLM factory.

Resolves a DB-stored ``LlmConfig`` row (decrypting the api key) into a cached
LangChain chat model. Models are OpenAI-compatible by default; new providers
can be registered with :func:`register_llm`.
"""
from __future__ import annotations

import json
from typing import Any, Callable

from langchain_core.language_models import BaseChatModel
from pydantic import BaseModel

from ..core.config import settings
from .providers import build_openai_compat

# Re-exported so callers can ``from app.llm import LLMBuildConfig``.
__all__ = ["LLMBuildConfig", "LLMFactory", "register_llm", "create_llm", "build_from_orm"]


class LLMBuildConfig(BaseModel):
    """A resolved (decrypted) spec for building a chat model."""

    provider: str
    model_name: str
    api_key: str = ""
    api_base_url: str = ""
    additional_params: dict[str, Any] = {}


Builder = Callable[[LLMBuildConfig], BaseChatModel]


class LLMFactory:
    """Registry + cache of chat models, keyed by config fingerprint."""

    _providers: dict[str, Builder] = {
        "openai": build_openai_compat,
        "deepseek": build_openai_compat,
        "tongyi": build_openai_compat,
        "ollama": build_openai_compat,
        "custom": build_openai_compat,
    }
    _cache: dict[str, BaseChatModel] = {}

    @classmethod
    def register_llm(cls, provider: str, builder: Builder) -> None:
        cls._providers[provider] = builder
        cls._cache.clear()

    @classmethod
    def create_llm(cls, cfg: LLMBuildConfig) -> BaseChatModel:
        key = cls._fingerprint(cfg)
        model = cls._cache.get(key)
        if model is None:
            builder = cls._providers.get(cfg.provider, build_openai_compat)
            model = builder(cfg)
            cls._cache[key] = model
        return model

    @staticmethod
    def _fingerprint(cfg: LLMBuildConfig) -> str:
        return json.dumps(
            {
                "provider": cfg.provider,
                "model": cfg.model_name,
                "base_url": cfg.api_base_url,
                "api_key": cfg.api_key,
                "params": cfg.additional_params,
            },
            sort_keys=True,
        )


def register_llm(provider: str, builder: Builder) -> None:
    LLMFactory.register_llm(provider, builder)


def create_llm(cfg: LLMBuildConfig) -> BaseChatModel:
    return LLMFactory.create_llm(cfg)


def build_from_orm(row) -> LLMBuildConfig:
    """Build a resolved config from a ``LlmConfig`` ORM row (decrypts api key)."""
    return LLMBuildConfig(
        provider=row.provider,
        model_name=row.model_name,
        api_base_url=row.api_base_url or "",
        api_key=settings.decrypt(row.api_key_encrypted),
        additional_params=row.additional_params or {},
    )
