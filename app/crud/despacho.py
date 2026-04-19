from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models.asignacion import Asignacion
from app.models.despacho import Despacho, DespachoEvento, EstadoDespacho
from app.models.viaje import Viaje
from app.schemas.despacho import (
    DespachoCreate,
    DespachoEventoCreate,
    DespachoRegistrarEntrega,
    DespachoRegistrarSalida,
    DespachoCerrar,
    DespachoUpdate,
)


def _detail_options():
    return (
        selectinload(Despacho.asignacion).selectinload(Asignacion.operador),
        selectinload(Despacho.asignacion).selectinload(Asignacion.unidad),
        selectinload(Despacho.asignacion).selectinload(Asignacion.viaje),
        selectinload(Despacho.flete),
        selectinload(Despacho.eventos),
    )


def get_by_id(db: Session, id_despacho: int) -> Despacho | None:
    stmt = select(Despacho).where(Despacho.id_despacho == id_despacho).options(*_detail_options())
    return db.execute(stmt).scalar_one_or_none()


def get_by_asignacion(db: Session, id_asignacion: int) -> Despacho | None:
    stmt = select(Despacho).where(Despacho.id_asignacion == id_asignacion).options(*_detail_options())
    return db.execute(stmt).scalar_one_or_none()


def list_despachos(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 100,
    estatus: EstadoDespacho | None = None,
    id_asignacion: int | None = None,
    id_flete: int | None = None,
) -> tuple[Sequence[Despacho], int]:
    stmt = (
        select(Despacho)
        .join(Asignacion, Despacho.id_asignacion == Asignacion.id_asignacion)
        .join(Viaje, Asignacion.id_viaje == Viaje.id)
        .options(*_detail_options())
    )
    count_stmt = select(func.count()).select_from(Despacho)

    if estatus is not None:
        stmt = stmt.where(Despacho.estatus == estatus)
        count_stmt = count_stmt.where(Despacho.estatus == estatus)
    if id_asignacion is not None:
        stmt = stmt.where(Despacho.id_asignacion == id_asignacion)
        count_stmt = count_stmt.where(Despacho.id_asignacion == id_asignacion)
    if id_flete is not None:
        stmt = stmt.where(Despacho.id_flete == id_flete)
        count_stmt = count_stmt.where(Despacho.id_flete == id_flete)

    total = db.execute(count_stmt).scalar_one()
    stmt = stmt.order_by(Viaje.codigo_viaje.asc(), Despacho.id_despacho.asc())
    stmt = stmt.offset(skip).limit(limit)
    return db.execute(stmt).scalars().all(), total


def create(db: Session, data: DespachoCreate) -> Despacho:
    obj = Despacho(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    full = get_by_id(db, obj.id_despacho)
    assert full is not None
    return full


def update(db: Session, despacho: Despacho, data: DespachoUpdate) -> Despacho:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(despacho, field, value)
    db.add(despacho)
    db.commit()
    db.refresh(despacho)
    full = get_by_id(db, despacho.id_despacho)
    assert full is not None
    return full


def registrar_salida(db: Session, despacho: Despacho, data: DespachoRegistrarSalida) -> Despacho:
    despacho.salida_real = data.salida_real
    despacho.km_salida = data.km_salida
    despacho.observaciones_salida = data.observaciones_salida
    despacho.estatus = EstadoDespacho.DESPACHADO
    db.add(despacho)
    db.commit()
    db.refresh(despacho)
    full = get_by_id(db, despacho.id_despacho)
    assert full is not None
    return full


def registrar_entrega(db: Session, despacho: Despacho, data: DespachoRegistrarEntrega) -> Despacho:
    despacho.fecha_entrega = data.fecha_entrega
    despacho.evidencia_entrega = data.evidencia_entrega
    despacho.firma_recibe = data.firma_recibe
    despacho.observaciones_entrega = data.observaciones_entrega
    despacho.estatus = EstadoDespacho.ENTREGADO
    db.add(despacho)
    db.commit()
    db.refresh(despacho)
    full = get_by_id(db, despacho.id_despacho)
    assert full is not None
    return full


def cerrar(db: Session, despacho: Despacho, data: DespachoCerrar) -> Despacho:
    despacho.llegada_real = data.llegada_real
    despacho.km_llegada = data.km_llegada
    despacho.observaciones_cierre = data.observaciones_cierre
    despacho.estatus = EstadoDespacho.CERRADO
    db.add(despacho)
    db.commit()
    db.refresh(despacho)
    full = get_by_id(db, despacho.id_despacho)
    assert full is not None
    return full


def cancelar(db: Session, despacho: Despacho, motivo_cancelacion: str) -> Despacho:
    despacho.motivo_cancelacion = motivo_cancelacion
    despacho.estatus = EstadoDespacho.CANCELADO
    db.add(despacho)
    db.commit()
    db.refresh(despacho)
    full = get_by_id(db, despacho.id_despacho)
    assert full is not None
    return full


def create_evento(db: Session, id_despacho: int, data: DespachoEventoCreate) -> DespachoEvento:
    obj = DespachoEvento(id_despacho=id_despacho, **data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def list_eventos(db: Session, id_despacho: int) -> tuple[Sequence[DespachoEvento], int]:
    stmt = (
        select(DespachoEvento)
        .where(DespachoEvento.id_despacho == id_despacho)
        .order_by(DespachoEvento.fecha_evento.desc(), DespachoEvento.id_evento.desc())
    )
    rows = db.execute(stmt).scalars().all()
    return rows, len(rows)


def delete(db: Session, despacho: Despacho) -> None:
    db.delete(despacho)
    db.commit()
