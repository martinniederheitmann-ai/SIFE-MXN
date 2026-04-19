from __future__ import annotations

from collections.abc import Sequence
from datetime import date

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.tarifa_compra_transportista import TarifaCompraTransportista
from app.models.tarifa_flete import AmbitoTarifaFlete, ModalidadCobroTarifa
from app.models.transportista import TipoTransportista
from app.crud.tarifa_flete import columna_coincide_lugar
from app.utils.lugares_match import lugares_equivalentes_para_tarifa
from app.schemas.tarifa_compra_transportista import (
    TarifaCompraTransportistaCreate,
    TarifaCompraTransportistaUpdate,
)


def get_by_id(db: Session, tarifa_id: int) -> TarifaCompraTransportista | None:
    return db.get(TarifaCompraTransportista, tarifa_id)


def list_tarifas(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 100,
    transportista_id: int | None = None,
    activo: bool | None = None,
    ambito: AmbitoTarifaFlete | None = None,
    modalidad_cobro: ModalidadCobroTarifa | None = None,
    tipo_transportista: TipoTransportista | None = None,
    buscar: str | None = None,
) -> tuple[Sequence[TarifaCompraTransportista], int]:
    stmt = select(TarifaCompraTransportista)
    count_stmt = select(func.count()).select_from(TarifaCompraTransportista)

    if transportista_id is not None:
        stmt = stmt.where(TarifaCompraTransportista.transportista_id == transportista_id)
        count_stmt = count_stmt.where(TarifaCompraTransportista.transportista_id == transportista_id)
    if activo is not None:
        stmt = stmt.where(TarifaCompraTransportista.activo == activo)
        count_stmt = count_stmt.where(TarifaCompraTransportista.activo == activo)
    if ambito is not None:
        stmt = stmt.where(TarifaCompraTransportista.ambito == ambito)
        count_stmt = count_stmt.where(TarifaCompraTransportista.ambito == ambito)
    if modalidad_cobro is not None:
        stmt = stmt.where(TarifaCompraTransportista.modalidad_cobro == modalidad_cobro)
        count_stmt = count_stmt.where(TarifaCompraTransportista.modalidad_cobro == modalidad_cobro)
    if tipo_transportista is not None:
        stmt = stmt.where(TarifaCompraTransportista.tipo_transportista == tipo_transportista)
        count_stmt = count_stmt.where(
            TarifaCompraTransportista.tipo_transportista == tipo_transportista
        )
    if buscar:
        pat = f"%{buscar.lower()}%"
        cond = or_(
            func.lower(TarifaCompraTransportista.nombre_tarifa).like(pat),
            func.lower(TarifaCompraTransportista.origen).like(pat),
            func.lower(TarifaCompraTransportista.destino).like(pat),
            func.lower(TarifaCompraTransportista.tipo_unidad).like(pat),
            func.lower(func.coalesce(TarifaCompraTransportista.tipo_carga, "")).like(pat),
        )
        stmt = stmt.where(cond)
        count_stmt = count_stmt.where(cond)

    total = db.execute(count_stmt).scalar_one()
    stmt = stmt.order_by(
        TarifaCompraTransportista.nombre_tarifa.asc(),
        TarifaCompraTransportista.id.asc(),
    ).offset(skip).limit(limit)
    return db.execute(stmt).scalars().all(), total


def create(db: Session, data: TarifaCompraTransportistaCreate) -> TarifaCompraTransportista:
    obj = TarifaCompraTransportista(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update(
    db: Session,
    tarifa: TarifaCompraTransportista,
    data: TarifaCompraTransportistaUpdate,
) -> TarifaCompraTransportista:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(tarifa, field, value)
    db.add(tarifa)
    db.commit()
    db.refresh(tarifa)
    return tarifa


def delete(db: Session, tarifa: TarifaCompraTransportista) -> None:
    db.delete(tarifa)
    db.commit()


def get_matching_tarifa(
    db: Session,
    *,
    transportista_id: int,
    ambito: AmbitoTarifaFlete | None,
    origen: str,
    destino: str,
    tipo_unidad: str,
    tipo_carga: str | None,
    tipo_transportista: TipoTransportista = TipoTransportista.SUBCONTRATADO,
    fecha_referencia: date | None = None,
) -> TarifaCompraTransportista | None:
    fecha = fecha_referencia or date.today()
    tu = (tipo_unidad or "").strip().lower()
    tc_norm = (tipo_carga or "").strip().lower()
    if tc_norm:
        tipo_carga_match = or_(
            TarifaCompraTransportista.tipo_carga.is_(None),
            func.lower(TarifaCompraTransportista.tipo_carga) == tc_norm,
        )
    else:
        tipo_carga_match = or_(
            TarifaCompraTransportista.tipo_carga.is_(None),
            func.lower(TarifaCompraTransportista.tipo_carga) == "general",
        )
    stmt = select(TarifaCompraTransportista).where(
        TarifaCompraTransportista.transportista_id == transportista_id,
        TarifaCompraTransportista.tipo_transportista == tipo_transportista,
        TarifaCompraTransportista.activo.is_(True),
        columna_coincide_lugar(TarifaCompraTransportista.origen, origen),
        columna_coincide_lugar(TarifaCompraTransportista.destino, destino),
        func.lower(func.trim(TarifaCompraTransportista.tipo_unidad)) == tu,
        tipo_carga_match,
        or_(
            TarifaCompraTransportista.vigencia_inicio.is_(None),
            TarifaCompraTransportista.vigencia_inicio <= fecha,
        ),
        or_(
            TarifaCompraTransportista.vigencia_fin.is_(None),
            TarifaCompraTransportista.vigencia_fin >= fecha,
        ),
    ).order_by(
        TarifaCompraTransportista.ambito != ambito
        if ambito is not None
        else TarifaCompraTransportista.id.is_(None),
        TarifaCompraTransportista.tipo_carga.is_(None),
        TarifaCompraTransportista.vigencia_inicio.desc(),
        TarifaCompraTransportista.id.desc(),
    )
    if ambito is not None:
        stmt = stmt.where(TarifaCompraTransportista.ambito == ambito)
    row = db.execute(stmt).scalars().first()
    if row is not None:
        return row
    stmt_wide = select(TarifaCompraTransportista).where(
        TarifaCompraTransportista.transportista_id == transportista_id,
        TarifaCompraTransportista.tipo_transportista == tipo_transportista,
        TarifaCompraTransportista.activo.is_(True),
        func.lower(func.trim(TarifaCompraTransportista.tipo_unidad)) == tu,
        tipo_carga_match,
        or_(
            TarifaCompraTransportista.vigencia_inicio.is_(None),
            TarifaCompraTransportista.vigencia_inicio <= fecha,
        ),
        or_(
            TarifaCompraTransportista.vigencia_fin.is_(None),
            TarifaCompraTransportista.vigencia_fin >= fecha,
        ),
    ).order_by(
        TarifaCompraTransportista.ambito != ambito
        if ambito is not None
        else TarifaCompraTransportista.id.is_(None),
        TarifaCompraTransportista.tipo_carga.is_(None),
        TarifaCompraTransportista.vigencia_inicio.desc(),
        TarifaCompraTransportista.id.desc(),
    )
    if ambito is not None:
        stmt_wide = stmt_wide.where(TarifaCompraTransportista.ambito == ambito)
    for cand in db.execute(stmt_wide.limit(200)).scalars().all():
        if lugares_equivalentes_para_tarifa(cand.origen, origen) and lugares_equivalentes_para_tarifa(
            cand.destino, destino
        ):
            return cand
    return None
