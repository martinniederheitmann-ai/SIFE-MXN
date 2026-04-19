from __future__ import annotations

import json
import time
from collections.abc import Sequence
from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.viaje import EstadoViaje, Viaje
from app.schemas.viaje import ViajeCreate, ViajeUpdate


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


def get_by_id(db: Session, viaje_id: int) -> Viaje | None:
    return db.get(Viaje, viaje_id)


def get_by_codigo(db: Session, codigo: str) -> Viaje | None:
    stmt = select(Viaje).where(Viaje.codigo_viaje == codigo)
    return db.execute(stmt).scalar_one_or_none()


def list_viajes(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 100,
    estado: EstadoViaje | None = None,
    origen_contains: str | None = None,
    destino_contains: str | None = None,
) -> tuple[Sequence[Viaje], int]:
    stmt = select(Viaje)
    count_stmt = select(func.count()).select_from(Viaje)

    if estado is not None:
        stmt = stmt.where(Viaje.estado == estado)
        count_stmt = count_stmt.where(Viaje.estado == estado)
    if origen_contains:
        pat = f"%{origen_contains.lower()}%"
        cond = func.lower(Viaje.origen).like(pat)
        stmt = stmt.where(cond)
        count_stmt = count_stmt.where(cond)
    if destino_contains:
        pat = f"%{destino_contains.lower()}%"
        cond = func.lower(Viaje.destino).like(pat)
        stmt = stmt.where(cond)
        count_stmt = count_stmt.where(cond)

    total = db.execute(count_stmt).scalar_one()
    stmt = stmt.order_by(Viaje.fecha_salida.desc(), Viaje.id.desc()).offset(skip).limit(limit)
    rows = db.execute(stmt).scalars().all()
    # #region agent log
    _agent_log(
        "crud/viaje.py:list_viajes",
        "list_viajes ok",
        {"total": int(total), "n_items": len(rows), "skip": skip, "limit": limit},
        "A",
    )
    # #endregion
    return rows, total


def create(db: Session, data: ViajeCreate) -> Viaje:
    obj = Viaje(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update(db: Session, viaje: Viaje, data: ViajeUpdate) -> Viaje:
    payload = data.model_dump(exclude_unset=True)
    for field, value in payload.items():
        setattr(viaje, field, value)
    db.add(viaje)
    db.commit()
    db.refresh(viaje)
    return viaje


def delete(db: Session, viaje: Viaje) -> None:
    db.delete(viaje)
    db.commit()
