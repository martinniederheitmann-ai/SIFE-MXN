from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.baja_dano import BajaDano
from app.schemas.baja_dano import BajaDanoCreate, BajaDanoUpdate


def get_by_id(db: Session, row_id: int) -> BajaDano | None:
    return db.get(BajaDano, row_id)


def list_rows(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 100,
    tipo: str | None = None,
    flete_id: int | None = None,
) -> tuple[Sequence[BajaDano], int]:
    stmt = select(BajaDano)
    count_stmt = select(func.count()).select_from(BajaDano)
    if tipo:
        stmt = stmt.where(BajaDano.tipo == tipo)
        count_stmt = count_stmt.where(BajaDano.tipo == tipo)
    if flete_id is not None:
        stmt = stmt.where(BajaDano.flete_id == flete_id)
        count_stmt = count_stmt.where(BajaDano.flete_id == flete_id)
    total = db.execute(count_stmt).scalar_one()
    stmt = stmt.order_by(BajaDano.fecha_evento.desc(), BajaDano.id.desc()).offset(skip).limit(limit)
    return db.execute(stmt).scalars().all(), total


def create(db: Session, data: BajaDanoCreate) -> BajaDano:
    obj = BajaDano(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update(db: Session, row: BajaDano, data: BajaDanoUpdate) -> BajaDano:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(row, field, value)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def delete(db: Session, row: BajaDano) -> None:
    db.delete(row)
    db.commit()
