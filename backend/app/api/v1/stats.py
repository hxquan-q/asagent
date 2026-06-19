"""Dashboard overview counts + recent activity."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict
from sqlmodel import Session, desc, func, select

from ...core.db import get_session
from ...core.deps import Principal, get_principal
from ...models import Agent, ApiKey, Conversation, Datasource, LlmConfig, Message, Skill

router = APIRouter(prefix="/stats", tags=["stats"])


class RecentConversation(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    agent_id: Optional[int] = None
    agent_name: Optional[str] = None
    created_at: datetime
    message_count: int = 0


class Overview(BaseModel):
    agents: int
    conversations: int
    messages: int
    datasources: int
    llm_configs: int
    skills: int
    api_keys: int
    enabled_skills: int
    recent_conversations: list[RecentConversation]


def _count(session: Session, model) -> int:
    return session.exec(select(func.count()).select_from(model)).one()


@router.get("/overview", response_model=Overview)
def overview(
    principal: Principal = Depends(get_principal),  # noqa: ARG001
    session: Session = Depends(get_session),
) -> Overview:
    agents = {a.id: a.name for a in session.exec(select(Agent)).all()}

    convs = session.exec(
        select(Conversation).order_by(desc(Conversation.created_at)).limit(6)
    ).all()
    ids = [c.id for c in convs]
    counts: dict[int, int] = {}
    if ids:
        rows = session.exec(
            select(Message.conversation_id, func.count())
            .where(Message.conversation_id.in_(ids))
            .group_by(Message.conversation_id)
        ).all()
        counts = {cid: cnt for cid, cnt in rows}

    return Overview(
        agents=_count(session, Agent),
        conversations=_count(session, Conversation),
        messages=_count(session, Message),
        datasources=_count(session, Datasource),
        llm_configs=_count(session, LlmConfig),
        skills=_count(session, Skill),
        api_keys=_count(session, ApiKey),
        enabled_skills=session.exec(
            select(func.count()).select_from(Skill).where(Skill.enabled == True)  # noqa: E712
        ).one(),
        recent_conversations=[
            RecentConversation(
                id=c.id,
                title=c.title or "新对话",
                agent_id=c.agent_id,
                agent_name=agents.get(c.agent_id) if c.agent_id else None,
                created_at=c.created_at,
                message_count=counts.get(c.id, 0),
            )
            for c in convs
        ],
    )
