"""Auth: console login (username/password -> JWT)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from ...core.db import get_session
from ...core.security import create_access_token, verify_password
from ...models import User

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginIn(BaseModel):
    username: str
    password: str


class LoginOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    is_admin: bool


@router.post("/login", response_model=LoginOut)
def login(body: LoginIn, session: Session = Depends(get_session)) -> LoginOut:
    user = session.exec(select(User).where(User.username == body.username)).first()
    if user is None or not verify_password(body.password, user.password_hash):
        raise HTTPException(401, "invalid credentials")
    return LoginOut(
        access_token=create_access_token(user.username),
        is_admin=user.is_admin,
    )
