"""Conversation history: list, read, rename, delete.

Messages have always been persisted by the chat endpoint; this router exposes
them so the console can show a conversation sidebar and reload past threads.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlmodel import Session, desc, select

from ...core.db import get_session
from ...core.deps import Principal, get_principal
from ...models import Agent, Conversation, Message

router = APIRouter(prefix="/conversations", tags=["conversations"])


def _text_of(message: Message) -> str:
    for b in message.blocks or []:
        if isinstance(b, dict) and b.get("type") == "text":
            return str(b.get("content", ""))
    # fall back to any block content
    for b in message.blocks or []:
        if isinstance(b, dict):
            return str(b.get("content") or b.get("title") or "")
    return ""


class ConversationSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    agent_id: Optional[int] = None
    agent_name: Optional[str] = None
    title: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    message_count: int = 0
    preview: str = ""


class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    role: str
    blocks: list[dict[str, Any]] = Field(default_factory=list)
    created_at: datetime


class ConversationDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    agent_id: Optional[int] = None
    agent_name: Optional[str] = None
    title: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    messages: list[MessageOut] = Field(default_factory=list)


class RenameIn(BaseModel):
    title: str = Field(min_length=1, max_length=256)


@router.get("", response_model=list[ConversationSummary])
def list_conversations(
    principal: Principal = Depends(get_principal),  # noqa: ARG001
    session: Session = Depends(get_session),
    limit: int = 100,
) -> list[ConversationSummary]:
    convs = session.exec(
        select(Conversation).order_by(desc(Conversation.created_at)).limit(limit)
    ).all()
    if not convs:
        return []

    agents = {a.id: a.name for a in session.exec(select(Agent)).all()}
    ids = [c.id for c in convs]
    msgs = session.exec(
        select(Message).where(Message.conversation_id.in_(ids)).order_by(Message.id)
    ).all()

    by_conv: dict[int, list[Message]] = {}
    for m in msgs:
        by_conv.setdefault(m.conversation_id, []).append(m)

    out: list[ConversationSummary] = []
    for c in convs:
        thread = by_conv.get(c.id, [])
        last = thread[-1] if thread else None
        preview = _text_of(last)[:140] if last else ""
        out.append(
            ConversationSummary(
                id=c.id,
                agent_id=c.agent_id,
                agent_name=agents.get(c.agent_id) if c.agent_id else None,
                title=c.title or "新对话",
                created_at=c.created_at,
                updated_at=last.created_at if last else c.created_at,
                message_count=len(thread),
                preview=preview,
            )
        )
    return out


@router.get("/{conversation_id}", response_model=ConversationDetail)
def get_conversation(
    conversation_id: int,
    principal: Principal = Depends(get_principal),  # noqa: ARG001
    session: Session = Depends(get_session),
) -> ConversationDetail:
    conv = session.get(Conversation, conversation_id)
    if conv is None:
        raise HTTPException(404, "conversation not found")
    agent_name = None
    if conv.agent_id:
        a = session.get(Agent, conv.agent_id)
        if a:
            agent_name = a.name
    msgs = session.exec(
        select(Message).where(Message.conversation_id == conv.id).order_by(Message.id)
    ).all()
    last_created = msgs[-1].created_at if msgs else conv.created_at
    return ConversationDetail(
        id=conv.id,
        agent_id=conv.agent_id,
        agent_name=agent_name,
        title=conv.title or "新对话",
        created_at=conv.created_at,
        updated_at=last_created,
        messages=[MessageOut.model_validate(m) for m in msgs],
    )


@router.patch("/{conversation_id}", response_model=ConversationSummary)
def rename_conversation(
    conversation_id: int,
    body: RenameIn,
    principal: Principal = Depends(get_principal),  # noqa: ARG001
    session: Session = Depends(get_session),
) -> Conversation:
    conv = session.get(Conversation, conversation_id)
    if conv is None:
        raise HTTPException(404, "conversation not found")
    conv.title = body.title.strip()
    session.add(conv)
    session.commit()
    session.refresh(conv)
    return conv


@router.delete("/{conversation_id}")
def delete_conversation(
    conversation_id: int,
    principal: Principal = Depends(get_principal),  # noqa: ARG001
    session: Session = Depends(get_session),
) -> dict:
    conv = session.get(Conversation, conversation_id)
    if conv is None:
        raise HTTPException(404, "conversation not found")
    for m in session.exec(
        select(Message).where(Message.conversation_id == conv.id)
    ).all():
        session.delete(m)
    session.delete(conv)
    session.commit()
    return {"ok": True}
