from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.role import Role
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


def list_users_ordered(db: Session) -> list[User]:
    stmt = select(User).options(joinedload(User.role)).order_by(User.username)
    return list(db.execute(stmt).scalars().unique().all())


def get_role_by_name(db: Session, name: str) -> Role | None:
    return db.execute(select(Role).where(Role.name == name)).scalar_one_or_none()


def create_user(
    db: Session,
    *,
    username: str,
    hashed_password: str,
    role_id: int,
    email: str | None,
    full_name: str | None,
) -> User:
    u = User(
        username=username,
        hashed_password=hashed_password,
        role_id=role_id,
        email=email,
        full_name=full_name,
        is_active=True,
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


def list_roles(db: Session) -> list[Role]:
    stmt = select(Role).order_by(Role.name)
    return list(db.execute(stmt).scalars().all())
