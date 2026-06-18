"""Agent CRUD (admin)."""
from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlmodel import Session, select

from ...core.db import get_session
from ...core.deps import require_admin
from ...models import Agent, User

router = APIRouter(prefix="/agents", tags=["agents"])


class AgentIn(BaseModel):
    name: str
    description: str = ""
    system_prompt: str = ""
    llm_config_id: int | None = None
    datasource_ids: list[int] = []
    tool_set: list[str] = []
    skill_ids: list[int] = []


class AgentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    description: str
    system_prompt: str
    llm_config_id: int | None
    datasource_ids: list[int]
    tool_set: list[str]
    skill_ids: list[int]
    created_at: datetime
    updated_at: datetime


def _apply(row: Agent, body: AgentIn) -> None:
    row.name = body.name
    row.description = body.description
    row.system_prompt = body.system_prompt
    row.llm_config_id = body.llm_config_id
    row.datasource_ids = body.datasource_ids
    row.tool_set = body.tool_set
    row.skill_ids = body.skill_ids


@router.get("", response_model=list[AgentOut])
def list_agents(
    admin: User = Depends(require_admin),  # noqa: ARG001
    session: Session = Depends(get_session),
) -> list[Agent]:
    return session.exec(select(Agent).order_by(Agent.created_at.desc())).all()


@router.post("", response_model=AgentOut)
def create_agent(
    body: AgentIn,
    admin: User = Depends(require_admin),  # noqa: ARG001
    session: Session = Depends(get_session),
) -> Agent:
    row = Agent()
    _apply(row, body)
    session.add(row)
    session.commit()
    session.refresh(row)
    return row


@router.put("/{agent_id}", response_model=AgentOut)
def update_agent(
    agent_id: int,
    body: AgentIn,
    admin: User = Depends(require_admin),  # noqa: ARG001
    session: Session = Depends(get_session),
) -> Agent:
    row = session.get(Agent, agent_id)
    if row is None:
        raise HTTPException(404, "agent not found")
    _apply(row, body)
    session.add(row)
    session.commit()
    session.refresh(row)
    return row


@router.delete("/{agent_id}")
def delete_agent(
    agent_id: int,
    admin: User = Depends(require_admin),  # noqa: ARG001
    session: Session = Depends(get_session),
) -> dict:
    row = session.get(Agent, agent_id)
    if row is None:
        raise HTTPException(404, "agent not found")
    session.delete(row)
    session.commit()
    return {"ok": True}
