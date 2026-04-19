from __future__ import annotations

from collections.abc import Sequence
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.gasto_viaje import GastoViaje
from app.schemas.gasto_viaje import GastoViajeCreate, GastoViajeUpdate


def get_by_id(db: Session, gasto_id: int) -> GastoViaje | None:
    return db.get(GastoViaje, gasto_id)


def list_gastos(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 100,
    flete_id: int | None = None,
) -> tuple[Sequence[GastoViaje], int]:
    stmt = select(GastoViaje)
    count_stmt = select(func.count()).select_from(GastoViaje)
    if flete_id is not None:
        stmt = stmt.where(GastoViaje.flete_id == flete_id)
        count_stmt = count_stmt.where(GastoViaje.flete_id == flete_id)
    total = db.execute(count_stmt).scalar_one()
    stmt = stmt.order_by(
        GastoViaje.tipo_gasto.asc(),
        func.coalesce(GastoViaje.descripcion, "").asc(),
        GastoViaje.id.asc(),
    ).offset(skip).limit(limit)
    return db.execute(stmt).scalars().all(), total


def create(db: Session, data: GastoViajeCreate) -> GastoViaje:
    obj = GastoViaje(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update(db: Session, gasto: GastoViaje, data: GastoViajeUpdate) -> GastoViaje:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(gasto, field, value)
    db.add(gasto)
    db.commit()
    db.refresh(gasto)
    return gasto


def delete(db: Session, gasto: GastoViaje) -> None:
    db.delete(gasto)
    db.commit()


def sum_gastos_by_flete(db: Session, flete_id: int) -> Decimal:
    total = db.execute(
        select(func.coalesce(func.sum(GastoViaje.monto), 0)).where(GastoViaje.flete_id == flete_id)
    ).scalar_one()
    return Decimal(total)
