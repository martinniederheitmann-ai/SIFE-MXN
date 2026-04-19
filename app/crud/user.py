from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.user import User


def get_by_username(db: Session, username: str) -> User | None:
    stmt = (
        select(User)
        .where(User.username == username)
        .options(joinedload(User.role))
    )
    return db.execute(stmt).scalar_one_or_none()


def get_by_id(db: Session, user_id: int) -> User | None:
    stmt = select(User).where(User.id == user_id).options(joinedload(User.role))
    return db.execute(stmt).scalar_one_or_none()
