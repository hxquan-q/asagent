"""Assemble a LangGraph ReAct agent from a stored Agent config.

Resolves the LLM (from llm_config_id, falling back to the default), picks the
tool set, injects skill metadata (Level-1 progressive disclosure) into the
system prompt, and compiles the graph.
"""
from __future__ import annotations

from typing import Any

from langgraph.prebuilt import create_react_agent
from sqlmodel import Session, select

from ..llm import build_from_orm, create_llm
from ..models import Agent, LlmConfig
from ..skills import SKILL_TOOLS, SkillRegistry
from ..tools import DEFAULT_TOOLS

DEFAULT_SYSTEM_PROMPT = """You are a capable data assistant connected to one or more PostgreSQL databases.

Workflow:
1. Use `describe_schema` to learn a datasource's tables/columns.
2. Write a read-only SELECT and run it with `query_database`.
3. Present results clearly: summarise in text AND use `visualize` / `make_table`-style tools (charts, diagrams, tables, files) as appropriate.

You also have access to Skills. When a task matches a skill below, first read its SKILL.md via `read_skill_file` to learn how to proceed, then (if needed) run its bundled scripts via `run_skill_script`. Skills may also dictate how to format your output.

Available skills:
{skills}
"""

_ALL_TOOLS = {t.name: t for t in [*DEFAULT_TOOLS, *SKILL_TOOLS]}


def resolve_tools(tool_set: list[str] | None) -> list[Any]:
    if not tool_set:
        return list(_ALL_TOOLS.values())
    return [_ALL_TOOLS[name] for name in tool_set if name in _ALL_TOOLS]


def build_system_prompt(agent: Agent) -> str:
    skills_md = SkillRegistry.prompt_metadata()
    base = (agent.system_prompt or "").strip()
    if not base:
        base = DEFAULT_SYSTEM_PROMPT
    if "{skills}" in base:
        return base.format(skills=skills_md)
    return f"{base}\n\nAvailable skills:\n{skills_md}"


def resolve_llm(agent: Agent, session: Session):
    row = None
    if agent.llm_config_id:
        row = session.get(LlmConfig, agent.llm_config_id)
    if row is None or not row.enabled:
        row = session.exec(
            select(LlmConfig).where(LlmConfig.is_default == True, LlmConfig.enabled == True)  # noqa: E712
        ).first()
    if row is None:
        raise ValueError("no enabled llm_config for this agent and no default configured")
    return create_llm(build_from_orm(row))


def build_agent(agent: Agent, session: Session):
    """Return (compiled_graph, datasource_ids) for the agent."""
    llm = resolve_llm(agent, session)
    tools = resolve_tools(agent.tool_set)
    prompt = build_system_prompt(agent)
    graph = create_react_agent(llm, tools, prompt=prompt)
    return graph, list(agent.datasource_ids or [])
