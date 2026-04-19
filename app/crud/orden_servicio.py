from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models.orden_servicio import EstatusOrdenServicio, OrdenServicio


def _options():
    return (
        selectinload(OrdenServicio.cliente),
        selectinload(OrdenServicio.cotizacion),
        selectinload(OrdenServicio.flete),
        selectinload(OrdenServicio.viaje),
        selectinload(OrdenServicio.despacho),
    )


def get_by_id(db: Session, orden_id: int) -> OrdenServicio | None:
    stmt = select(OrdenServicio).where(OrdenServicio.id == orden_id).options(*_options())
    return db.execute(stmt).scalar_one_or_none()


def get_by_folio(db: Session, folio: str) -> OrdenServicio | None:
    stmt = select(OrdenServicio).where(OrdenServicio.folio == folio).options(*_options())
    return db.execute(stmt).scalar_one_or_none()


def next_folio(db: Session) -> str:
    prefix = datetime.now().strftime("OS%Y%m%d")
    stmt = select(func.count()).select_from(OrdenServicio).where(
        OrdenServicio.folio.like(f"{prefix}%")
    )
    count = db.execute(stmt).scalar_one()
    return f"{prefix}-{count + 1:04d}"


def list_ordenes(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 100,
    cliente_id: int | None = None,
    estatus: EstatusOrdenServicio | None = None,
) -> tuple[Sequence[OrdenServicio], int]:
    stmt = select(OrdenServicio).options(*_options())
    count_stmt = select(func.count()).select_from(OrdenServicio)
    if cliente_id is not None:
        stmt = stmt.where(OrdenServicio.cliente_id == cliente_id)
        count_stmt = count_stmt.where(OrdenServicio.cliente_id == cliente_id)
    if estatus is not None:
        stmt = stmt.where(OrdenServicio.estatus == estatus)
        count_stmt = count_stmt.where(OrdenServicio.estatus == estatus)
    total = db.execute(count_stmt).scalar_one()
    stmt = stmt.order_by(OrdenServicio.folio.asc(), OrdenServicio.id.asc())
    stmt = stmt.offset(skip).limit(limit)
    return db.execute(stmt).scalars().all(), total


def create(db: Session, payload: dict) -> OrdenServicio:
    row = OrdenServicio(**payload)
    db.add(row)
    db.commit()
    db.refresh(row)
    full = get_by_id(db, row.id)
    assert full is not None
    return full


def update(db: Session, row: OrdenServicio, payload: dict) -> OrdenServicio:
    for key, value in payload.items():
        setattr(row, key, value)
    db.add(row)
    db.commit()
    db.refresh(row)
    full = get_by_id(db, row.id)
    assert full is not None
    return full


def change_status(
    db: Session, row: OrdenServicio, estatus: EstatusOrdenServicio, observaciones: str | None
) -> OrdenServicio:
    row.estatus = estatus
    if observaciones is not None:
        row.observaciones = observaciones
    db.add(row)
    db.commit()
    db.refresh(row)
    full = get_by_id(db, row.id)
    assert full is not None
    return full


def delete(db: Session, row: OrdenServicio) -> None:
    db.delete(row)
    db.commit()
