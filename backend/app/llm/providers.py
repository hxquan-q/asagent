"""Default LLM providers + builders.

Every provider maps to an OpenAI-compatible ``ChatOpenAI`` instance via the
right ``base_url`` / ``api_key``. Additional providers can be registered with
``LLMFactory.register_llm`` (e.g. a native ``ChatTongyi`` / ``ChatOllama``).
"""
from __future__ import annotations

from typing import Any

from langchain_core.language_models import BaseChatModel

from .openai_compat import CompatChatOpenAI

# Default OpenAI-compatible base URLs per provider (used when a config has none).
PROVIDER_DEFAULTS: dict[str, str] = {
    "openai": "https://api.openai.com/v1",
    "deepseek": "https://api.deepseek.com",
    "tongyi": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "ollama": "http://localhost:11434/v1",
    "custom": "",
}


def build_openai_compat(cfg) -> BaseChatModel:
    """Build an OpenAI-compatible chat model from a resolved config."""
    kwargs: dict[str, Any] = {"model": cfg.model_name}

    base_url = cfg.api_base_url or PROVIDER_DEFAULTS.get(cfg.provider, "")
    if base_url:
        kwargs["base_url"] = base_url

    api_key = cfg.api_key
    if not api_key and cfg.provider == "ollama":
        api_key = "ollama"  # Ollama /v1 ignores the key but the SDK needs non-empty
    if api_key:
        kwargs["api_key"] = api_key

    # additional_params: temperature, max_tokens, extra_body, etc.
    for k, v in (cfg.additional_params or {}).items():
        kwargs[k] = v

    return CompatChatOpenAI(**kwargs)
