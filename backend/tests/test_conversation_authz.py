"""Authorization tests for conversation history scoping + agent listing.

Guards the fix where conversation list/get/rename/delete are scoped to the
caller (console JWT vs external API key), and where agent listing is
admin-only. A regression here is a cross-tenant data leak (IDOR).
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.core.db import get_engine
from app.main import app
from app.models import Conversation, Message


@pytest.fixture()
def client() -> TestClient:
    # Context-manager form triggers the app lifespan (init_db + seed_admin).
    with TestClient(app) as c:
        yield c


@pytest.fixture()
def admin_token(client: TestClient) -> str:
    resp = client.post(
        "/api/v1/auth/login",
        json={"username": settings.ADMIN_USERNAME, "password": settings.ADMIN_PASSWORD},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


@pytest.fixture()
def api_key(client: TestClient, admin_token: str) -> str:
    resp = client.post(
        "/api/v1/apikeys",
        json={"name": "test-key"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["full_key"]


def _make_conversation(*, api_key_id: int | None, title: str) -> int:
    """Insert a conversation (+ one message) directly, owned as specified."""
    with Session(get_engine()) as session:
        conv = Conversation(title=title, api_key_id=api_key_id)
        session.add(conv)
        session.commit()
        session.refresh(conv)
        session.add(
            Message(
                conversation_id=conv.id,
                role="user",
                blocks=[{"type": "text", "content": "hi"}],
            )
        )
        session.commit()
        return conv.id


def _api_key_id(full_key: str) -> int:
    from app.core.security import hash_api_key
    from app.models import ApiKey
    from sqlmodel import select

    with Session(get_engine()) as session:
        ak = session.exec(
            select(ApiKey).where(ApiKey.key_hash == hash_api_key(full_key))
        ).first()
        assert ak is not None
        return ak.id


def test_console_sees_only_console_conversations(client: TestClient, admin_token: str, api_key: str):
    """Console (JWT) lists api_key_id IS NULL conversations, not API-key ones."""
    console_id = _make_conversation(api_key_id=None, title="console-thread")
    key_owned_id = _make_conversation(api_key_id=_api_key_id(api_key), title="key-thread")

    resp = client.get("/api/v1/conversations", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200, resp.text
    ids = {c["id"] for c in resp.json()}
    assert console_id in ids
    assert key_owned_id not in ids


def test_api_key_sees_only_its_own_conversations(client: TestClient, api_key: str):
    """An API key lists only conversations it created."""
    console_id = _make_conversation(api_key_id=None, title="console-thread")
    key_owned_id = _make_conversation(api_key_id=_api_key_id(api_key), title="key-thread")

    resp = client.get("/api/v1/conversations", headers={"X-API-Key": api_key})
    assert resp.status_code == 200, resp.text
    ids = {c["id"] for c in resp.json()}
    assert key_owned_id in ids
    assert console_id not in ids


def test_api_key_cannot_read_console_conversation(client: TestClient, api_key: str):
    console_id = _make_conversation(api_key_id=None, title="secret-console")
    resp = client.get(f"/api/v1/conversations/{console_id}", headers={"X-API-Key": api_key})
    assert resp.status_code == 404  # 404 (not 403) to avoid enumeration


def test_api_key_cannot_delete_or_rename_console_conversation(client: TestClient, admin_token: str, api_key: str):
    console_id = _make_conversation(api_key_id=None, title="protected")

    assert client.delete(
        f"/api/v1/conversations/{console_id}", headers={"X-API-Key": api_key}
    ).status_code == 404
    assert client.patch(
        f"/api/v1/conversations/{console_id}",
        json={"title": "hijacked"},
        headers={"X-API-Key": api_key},
    ).status_code == 404

    # still readable + unchanged for the rightful console owner
    resp = client.get(f"/api/v1/conversations/{console_id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200
    assert resp.json()["title"] == "protected"


def test_agent_list_requires_admin(client: TestClient, admin_token: str, api_key: str):
    """Agent listing is admin-only: API keys get rejected, console admin succeeds."""
    assert client.get("/api/v1/agents", headers={"X-API-Key": api_key}).status_code in (401, 403)
    assert client.get("/api/v1/agents", headers={"Authorization": f"Bearer {admin_token}"}).status_code == 200
