"""OpenAI-compatible chat model.

All configured providers (OpenAI, DeepSeek, Tongyi/DashScope OpenAI-compat,
Ollama ``/v1``, and arbitrary custom OpenAI-compatible endpoints) are served by
``ChatOpenAI`` from ``langchain_openai`` — it natively supports streaming and
tool calling against any OpenAI-compatible ``base_url``.

``CompatChatOpenAI`` is the extension point for surfacing *reasoning* tokens
(DeepSeek ``reasoning_content`` / Ollama & LMStudio ``reasoning``) during
streaming. Today it behaves as ``ChatOpenAI``; the override is added in the
optimisation pass once verified against a live endpoint (see SQLBot
``backend/apps/ai_model/openai/llm.py`` for the ``_stream`` /
``_convert_chunk_to_generation_chunk`` pattern).
"""
from __future__ import annotations

from langchain_openai import ChatOpenAI


class CompatChatOpenAI(ChatOpenAI):
    """Drop-in ``ChatOpenAI``; reserved for reasoning-token compatibility."""
    pass
