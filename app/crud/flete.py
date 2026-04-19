from __future__ import annotations

import json
import time
from collections.abc import Sequence
from decimal import Decimal
from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models.flete import EstadoFlete, Flete
from app.schemas.flete import FleteCreate, FleteUpdate

_FLETE_LOAD = (
    selectinload(Flete.cliente),
    selectinload(Flete.transportista),
    selectinload(Flete.viaje),
)


def _agent_log(location: str, message: str, data: dict, hypothesis_id: str) -> None:
    # #region agent log
    payload = {
        "sessionId": "feec30",
        "timestamp": int(time.time() * 1000),
        "location": location,
        "message": message,
        "data": data,
        "hypothesisId": hypothesis_id,
    }
    try:
        p = Path(__file__).resolve().parents[2] / "debug-feec30.log"
        with p.open("a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")
    except OSError:
        pass
    # #endregion


def get_by_id(db: Session, flete_id: int) -> Flete | None:
    stmt = select(Flete).where(Flete.id == flete_id).options(*_FLETE_LOAD)
    return db.execute(stmt).scalar_one_or_none()


def get_by_codigo(db: Session, codigo: str) -> Flete | None:
    stmt = select(Flete).where(Flete.codigo_flete == codigo).options(*_FLETE_LOAD)
    return db.execute(stmt).scalar_one_or_none()


def list_fletes(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 100,
    estado: EstadoFlete | None = None,
    cliente_id: int | None = None,
    transportista_id: int | None = None,
) -> tuple[Sequence[Flete], int]:
    stmt = select(Flete).options(*_FLETE_LOAD)
    count_stmt = select(func.count()).select_from(Flete)

    if estado is not None:
        stmt = stmt.where(Flete.estado == estado)
        count_stmt = count_stmt.where(Flete.estado == estado)
    if cliente_id is not None:
        stmt = stmt.where(Flete.cliente_id == cliente_id)
        count_stmt = count_stmt.where(Flete.cliente_id == cliente_id)
    if transportista_id is not None:
        stmt = stmt.where(Flete.transportista_id == transportista_id)
        count_stmt = count_stmt.where(Flete.transportista_id == transportista_id)

    total = db.execute(count_stmt).scalar_one()
    stmt = stmt.order_by(Flete.created_at.desc(), Flete.id.desc()).offset(skip).limit(limit)
    rows = db.execute(stmt).scalars().all()
    # #region agent log
    _agent_log(
        "crud/flete.py:list_fletes",
        "list_fletes ok",
        {"total": int(total), "n_items": len(rows), "skip": skip, "limit": limit},
        "A",
    )
    # #endregion
    return rows, total


def _sync_margenes_flete_row(flete: Flete) -> None:
    """precio_venta - costo_*; el margen no se toma del cliente."""
    if flete.precio_venta is not None and flete.costo_transporte_estimado is not None:
        flete.margen_estimado = (flete.precio_venta - flete.costo_transporte_estimado).quantize(
            Decimal("0.01")
        )
    else:
        flete.margen_estimado = None
    if flete.precio_venta is not None and flete.costo_transporte_real is not None:
        flete.margen_real = (flete.precio_venta - flete.costo_transporte_real).quantize(Decimal("0.01"))
    else:
        flete.margen_real = None


def sync_real_cost_from_gastos(db: Session, flete: Flete, total_gastos: Decimal) -> None:
    """Actualiza costo real desde suma de gastos y recalcula margen real."""
    flete.costo_transporte_real = total_gastos.quantize(Decimal("0.01"))
    _sync_margenes_flete_row(flete)
    db.add(flete)
    db.commit()
    db.refresh(flete)


def create(db: Session, data: FleteCreate) -> Flete:
    obj = Flete(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    full = get_by_id(db, obj.id)
    assert full is not None
    return full


def update(db: Session, flete: Flete, data: FleteUpdate) -> Flete:
    payload = data.model_dump(exclude_unset=True)
    for field, value in payload.items():
        setattr(flete, field, value)
    _sync_margenes_flete_row(flete)
    db.add(flete)
    db.commit()
    db.refresh(flete)
    full = get_by_id(db, flete.id)
    assert full is not None
    return full


def delete(db: Session, flete: Flete) -> None:
    db.delete(flete)
    db.commit()
