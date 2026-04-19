"""Persistencia de cotizaciones de flete (historial y conversión a flete)."""

from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models.cotizacion_flete import CotizacionFlete, EstatusCotizacionFlete


def _options():
    return (
        selectinload(CotizacionFlete.cliente),
        selectinload(CotizacionFlete.tarifa_flete),
        selectinload(CotizacionFlete.flete),
    )


def get_by_id(db: Session, cotizacion_id: int) -> CotizacionFlete | None:
    stmt = select(CotizacionFlete).where(CotizacionFlete.id == cotizacion_id).options(*_options())
    return db.execute(stmt).scalar_one_or_none()


def next_folio(db: Session) -> str:
    total = db.execute(select(func.count()).select_from(CotizacionFlete)).scalar_one()
    return f"COT-{total + 1:05d}"


def create(db: Session, payload: dict) -> CotizacionFlete:
    row = CotizacionFlete(**payload)
    db.add(row)
    db.commit()
    db.refresh(row)
    full = get_by_id(db, row.id)
    assert full is not None
    return full


def list_cotizaciones(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 100,
    cliente_id: int | None = None,
    estatus: EstatusCotizacionFlete | None = None,
) -> tuple[Sequence[CotizacionFlete], int]:
    stmt = select(CotizacionFlete).options(*_options())
    count_stmt = select(func.count()).select_from(CotizacionFlete)
    if cliente_id is not None:
        stmt = stmt.where(CotizacionFlete.cliente_id == cliente_id)
        count_stmt = count_stmt.where(CotizacionFlete.cliente_id == cliente_id)
    if estatus is not None:
        stmt = stmt.where(CotizacionFlete.estatus == estatus)
        count_stmt = count_stmt.where(CotizacionFlete.estatus == estatus)
    total = db.execute(count_stmt).scalar_one()
    stmt = (
        stmt.order_by(CotizacionFlete.created_at.desc(), CotizacionFlete.id.desc())
        .offset(skip)
        .limit(limit)
    )
    return db.execute(stmt).scalars().all(), total


def update_status(
    db: Session,
    row: CotizacionFlete,
    *,
    estatus: EstatusCotizacionFlete,
    observaciones: str | None = None,
) -> CotizacionFlete:
    row.estatus = estatus
    if observaciones is not None:
        row.observaciones = observaciones
    db.add(row)
    db.commit()
    db.refresh(row)
    full = get_by_id(db, row.id)
    assert full is not None
    return full


def mark_converted(db: Session, cotizacion: CotizacionFlete, flete_id: int) -> CotizacionFlete:
    cotizacion.flete_id = flete_id
    cotizacion.estatus = EstatusCotizacionFlete.CONVERTIDA
    db.add(cotizacion)
    db.commit()
    db.refresh(cotizacion)
    full = get_by_id(db, cotizacion.id)
    assert full is not None
    return full
