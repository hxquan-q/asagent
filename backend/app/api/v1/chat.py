"""Chat endpoint: SSE streaming + sync (JSON) over a configured agent."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from langchain_core.messages import AIMessage, HumanMessage
from pydantic import BaseModel
from sqlmodel import Session, select

from ...agent import build_agent, run_stream, sse
from ...core.db import get_engine, get_session
from ...core.deps import Principal, get_principal
from ...models import Agent, Conversation, Message

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    agent_id: int
    message: str
    conversation_id: int | None = None


def _history_from_messages(msgs: list[Message]) -> list:
    out = []
    for m in msgs:
        text = "".join(
            b.get("content", "")
            for b in (m.blocks or [])
            if isinstance(b, dict) and b.get("type") == "text"
        )
        if m.role == "user":
            out.append(HumanMessage(content=text))
        elif m.role == "assistant" and text:
            out.append(AIMessage(content=text))
    return out


def _load_or_create_conversation(body: ChatRequest, agent: Agent, principal: Principal, session: Session):
    history: list = []
    if body.conversation_id:
        conv = session.get(Conversation, body.conversation_id)
        if conv is not None:
            msgs = session.exec(
                select(Message).where(Message.conversation_id == conv.id).order_by(Message.id)
            ).all()
            history = _history_from_messages(msgs)
        return conv, history
    return None, history


@router.post("")
def chat(
    body: ChatRequest,
    principal: Principal = Depends(get_principal),
    session: Session = Depends(get_session),
) -> StreamingResponse:
    agent = session.get(Agent, body.agent_id)
    if agent is None:
        raise HTTPException(404, "agent not found")

    conv, history = _load_or_create_conversation(body, agent, principal, session)
    if conv is None:
        conv = Conversation(
            agent_id=agent.id,
            api_key_id=principal.api_key.id if principal.api_key else None,
            title=body.message[:80],
        )
        session.add(conv)
        session.commit()
        session.refresh(conv)
    session.add(Message(
        conversation_id=conv.id, role="user",
        blocks=[{"type": "text", "content": body.message}],
    ))
    session.commit()

    graph, ds_ids = build_agent(agent, session)
    conv_id = conv.id
    user_msg = body.message
    hist = history

    def gen():
        yield sse({"type": "conversation", "conversation_id": conv_id})
        text_acc: list[str] = []
        blocks: list[dict] = []
        for ev in run_stream(graph, user_msg, ds_ids, history=hist):
            yield sse(ev)
            if ev["type"] == "token":
                text_acc.append(ev["content"])
            elif ev["type"] == "block":
                blocks.append(ev["block"])
        with Session(get_engine()) as s2:
            s2.add(Message(
                conversation_id=conv_id, role="assistant",
                blocks=[{"type": "text", "content": "".join(text_acc)}, *blocks],
            ))
            s2.commit()

    return StreamingResponse(gen(), media_type="text/event-stream")


@router.post("/sync")
def chat_sync(
    body: ChatRequest,
    principal: Principal = Depends(get_principal),
    session: Session = Depends(get_session),
) -> dict:
    agent = session.get(Agent, body.agent_id)
    if agent is None:
        raise HTTPException(404, "agent not found")
    conv, history = _load_or_create_conversation(body, agent, principal, session)
    graph, ds_ids = build_agent(agent, session)

    text_acc: list[str] = []
    blocks: list[dict] = []
    for ev in run_stream(graph, body.message, ds_ids, history=history):
        if ev["type"] == "token":
            text_acc.append(ev["content"])
        elif ev["type"] == "block":
            blocks.append(ev["block"])
        elif ev["type"] == "error":
            raise HTTPException(500, ev.get("content", "agent error"))

    assistant_blocks = [{"type": "text", "content": "".join(text_acc)}, *blocks]
    with Session(get_engine()) as s2:
        new_conv = conv or Conversation(
            agent_id=agent.id,
            api_key_id=principal.api_key.id if principal.api_key else None,
            title=body.message[:80],
        )
        s2.add(new_conv)
        s2.commit()
        s2.refresh(new_conv)
        s2.add(Message(conversation_id=new_conv.id, role="user",
                       blocks=[{"type": "text", "content": body.message}]))
        s2.add(Message(conversation_id=new_conv.id, role="assistant", blocks=assistant_blocks))
        s2.commit()
        return {"conversation_id": new_conv.id, "blocks": assistant_blocks}
