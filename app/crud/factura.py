from __future__ import annotations

from collections.abc import Sequence
from decimal import Decimal

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.factura import Factura
from app.schemas.factura import FacturaCreate, FacturaUpdate


def get_by_id(db: Session, factura_id: int) -> Factura | None:
    stmt = (
        select(Factura)
        .where(Factura.id == factura_id)
        .options(
            selectinload(Factura.cliente),
            selectinload(Factura.flete),
            selectinload(Factura.orden_servicio),
        )
    )
    return db.execute(stmt).scalar_one_or_none()


def list_facturas(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 100,
    cliente_id: int | None = None,
    estatus: str | None = None,
    buscar: str | None = None,
) -> tuple[Sequence[Factura], int]:
    stmt = select(Factura).options(
        selectinload(Factura.cliente),
        selectinload(Factura.flete),
        selectinload(Factura.orden_servicio),
    )
    count_stmt = select(func.count()).select_from(Factura)

    if cliente_id is not None:
        stmt = stmt.where(Factura.cliente_id == cliente_id)
        count_stmt = count_stmt.where(Factura.cliente_id == cliente_id)
    if estatus is not None:
        stmt = stmt.where(Factura.estatus == estatus)
        count_stmt = count_stmt.where(Factura.estatus == estatus)
    if buscar:
        pat = f"%{buscar.lower()}%"
        cond = or_(
            func.lower(Factura.folio).like(pat),
            func.lower(func.coalesce(Factura.serie, "")).like(pat),
            func.lower(Factura.concepto).like(pat),
            func.lower(func.coalesce(Factura.referencia, "")).like(pat),
        )
        stmt = stmt.where(cond)
        count_stmt = count_stmt.where(cond)

    total = db.execute(count_stmt).scalar_one()
    stmt = stmt.order_by(
        func.coalesce(Factura.serie, "").asc(),
        Factura.folio.asc(),
        Factura.id.asc(),
    ).offset(skip).limit(limit)
    return db.execute(stmt).scalars().all(), total


def next_folio(db: Session) -> str:
    total = db.execute(select(func.count()).select_from(Factura)).scalar_one()
    return f"FAC-{total + 1:05d}"


def _sync_financial_fields(payload: dict, current: Factura | None = None) -> dict:
    subtotal = payload.get("subtotal")
    if subtotal is None and current is not None:
        subtotal = current.subtotal
    iva_pct = payload.get("iva_pct")
    if iva_pct is None and current is not None:
        iva_pct = current.iva_pct
    retencion = payload.get("retencion_monto")
    if retencion is None:
        retencion = current.retencion_monto if current is not None else Decimal("0")
    iva_monto = payload.get("iva_monto")
    if iva_monto is None and subtotal is not None and iva_pct is not None:
        iva_monto = subtotal * iva_pct
    total = payload.get("total")
    if total is None and subtotal is not None and iva_monto is not None:
        total = subtotal + iva_monto - retencion
    saldo = payload.get("saldo_pendiente")
    if saldo is None and current is not None:
        saldo = current.saldo_pendiente if "total" not in payload and "subtotal" not in payload else total
    elif saldo is None:
        saldo = total
    payload["iva_monto"] = iva_monto
    payload["total"] = total
    payload["saldo_pendiente"] = saldo
    return payload


def create(db: Session, data: FacturaCreate | dict) -> Factura:
    payload = data.model_dump() if isinstance(data, FacturaCreate) else dict(data)
    payload = _sync_financial_fields(payload)
    obj = Factura(**payload)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    full = get_by_id(db, obj.id)
    assert full is not None
    return full


def update(db: Session, factura: Factura, data: FacturaUpdate) -> Factura:
    payload = _sync_financial_fields(data.model_dump(exclude_unset=True), factura)
    for field, value in payload.items():
        setattr(factura, field, value)
    db.add(factura)
    db.commit()
    db.refresh(factura)
    full = get_by_id(db, factura.id)
    assert full is not None
    return full


def delete(db: Session, factura: Factura) -> None:
    db.delete(factura)
    db.commit()
