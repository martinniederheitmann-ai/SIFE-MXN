from __future__ import annotations

import re
from collections.abc import Sequence
from datetime import date

from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session

from app.models.tarifa_flete import AmbitoTarifaFlete, ModalidadCobroTarifa, TarifaFlete
from app.models.transportista import TipoTransportista
from app.schemas.tarifa_flete import TarifaFleteCreate, TarifaFleteUpdate
from app.utils.lugares_match import lugares_equivalentes_para_tarifa


def _tipo_unidad_normalizada(s: str | None) -> str:
    """Quita espacios para alinear 'tracto camion' con 'tractocamion'."""
    t = (s or "").strip().lower()
    return re.sub(r"\s+", "", t)


def _fila_coincide_tipo_carga(cand: TarifaFlete, tc_norm: str) -> bool:
    raw = (cand.tipo_carga or "").strip().lower() if cand.tipo_carga else ""
    if not tc_norm:
        return raw == "" or raw == "general"
    if not raw:
        return True
    return raw == tc_norm


def get_by_id(db: Session, tarifa_id: int) -> TarifaFlete | None:
    return db.get(TarifaFlete, tarifa_id)


def get_active_duplicate_nombre(
    db: Session,
    nombre_tarifa: str,
    *,
    exclude_id: int | None = None,
) -> TarifaFlete | None:
    """Otra tarifa activa con el mismo nombre (sin distinguir mayúsculas; tras trim)."""
    key = (nombre_tarifa or "").strip().lower()
    if not key:
        return None
    stmt = select(TarifaFlete).where(
        TarifaFlete.activo.is_(True),
        func.lower(func.trim(TarifaFlete.nombre_tarifa)) == key,
    )
    if exclude_id is not None:
        stmt = stmt.where(TarifaFlete.id != exclude_id)
    return db.execute(stmt).scalars().first()


def list_tarifas(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 100,
    activo: bool | None = None,
    ambito: AmbitoTarifaFlete | None = None,
    modalidad_cobro: ModalidadCobroTarifa | None = None,
    tipo_operacion: TipoTransportista | None = None,
    buscar: str | None = None,
) -> tuple[Sequence[TarifaFlete], int]:
    stmt = select(TarifaFlete)
    count_stmt = select(func.count()).select_from(TarifaFlete)

    if activo is not None:
        stmt = stmt.where(TarifaFlete.activo == activo)
        count_stmt = count_stmt.where(TarifaFlete.activo == activo)
    if ambito is not None:
        stmt = stmt.where(TarifaFlete.ambito == ambito)
        count_stmt = count_stmt.where(TarifaFlete.ambito == ambito)
    if modalidad_cobro is not None:
        stmt = stmt.where(TarifaFlete.modalidad_cobro == modalidad_cobro)
        count_stmt = count_stmt.where(TarifaFlete.modalidad_cobro == modalidad_cobro)
    if tipo_operacion is not None:
        stmt = stmt.where(TarifaFlete.tipo_operacion == tipo_operacion)
        count_stmt = count_stmt.where(TarifaFlete.tipo_operacion == tipo_operacion)
    if buscar:
        pat = f"%{buscar.lower()}%"
        cond = or_(
            func.lower(TarifaFlete.nombre_tarifa).like(pat),
            func.lower(TarifaFlete.origen).like(pat),
            func.lower(TarifaFlete.destino).like(pat),
            func.lower(TarifaFlete.tipo_unidad).like(pat),
            func.lower(func.coalesce(TarifaFlete.tipo_carga, "")).like(pat),
        )
        stmt = stmt.where(cond)
        count_stmt = count_stmt.where(cond)

    total = db.execute(count_stmt).scalar_one()
    stmt = stmt.order_by(TarifaFlete.nombre_tarifa.asc(), TarifaFlete.id.asc()).offset(skip).limit(limit)
    return db.execute(stmt).scalars().all(), total


def create(db: Session, data: TarifaFleteCreate) -> TarifaFlete:
    obj = TarifaFlete(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update(db: Session, tarifa: TarifaFlete, data: TarifaFleteUpdate) -> TarifaFlete:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(tarifa, field, value)
    db.add(tarifa)
    db.commit()
    db.refresh(tarifa)
    return tarifa


def delete(db: Session, tarifa: TarifaFlete) -> None:
    db.delete(tarifa)
    db.commit()


def lugar_key_ciudad(texto: str | None) -> str:
    """Primera parte antes de coma (ciudad sin estado), para alinear viaje y tarifa."""
    t = (texto or "").strip()
    if not t:
        return ""
    return t.split(",")[0].strip().lower()


def columna_coincide_lugar(column, texto_solicitud: str):
    """
    Coincide columna de catalogo con texto del viaje/solicitud:
    igualdad tras trim (minúsculas), o misma ciudad base (antes de coma),
    o catalogo con sufijo de estado (ej. "veracruz" solicitud vs "veracruz, ver." en tarifa).
    """
    full = (texto_solicitud or "").strip().lower()
    key = lugar_key_ciudad(texto_solicitud)
    col_norm = func.lower(func.trim(column))
    conds = [col_norm == full]
    if key:
        conds.append(col_norm == key)
        conds.append(col_norm.like(key + ",%"))
    return or_(*conds) if len(conds) > 1 else conds[0]


def get_matching_tarifa(
    db: Session,
    *,
    ambito: AmbitoTarifaFlete | None,
    origen: str,
    destino: str,
    tipo_unidad: str,
    tipo_carga: str | None,
    tipo_operacion: TipoTransportista = TipoTransportista.SUBCONTRATADO,
    fecha_referencia: date | None = None,
) -> TarifaFlete | None:
    fecha = fecha_referencia or date.today()
    tu = (tipo_unidad or "").strip().lower()
    tc_norm = (tipo_carga or "").strip().lower()
    if tc_norm:
        tipo_carga_match = or_(
            TarifaFlete.tipo_carga.is_(None),
            func.lower(TarifaFlete.tipo_carga) == tc_norm,
        )
    else:
        # Sin tipo de carga en la peticion: coincide con tarifa generica (NULL) o "general" habitual.
        tipo_carga_match = or_(
            TarifaFlete.tipo_carga.is_(None),
            func.lower(TarifaFlete.tipo_carga) == "general",
        )
    stmt = select(TarifaFlete).where(
        TarifaFlete.activo.is_(True),
        TarifaFlete.tipo_operacion == tipo_operacion,
        columna_coincide_lugar(TarifaFlete.origen, origen),
        columna_coincide_lugar(TarifaFlete.destino, destino),
        func.lower(func.trim(TarifaFlete.tipo_unidad)) == tu,
        tipo_carga_match,
        or_(TarifaFlete.vigencia_inicio.is_(None), TarifaFlete.vigencia_inicio <= fecha),
        or_(TarifaFlete.vigencia_fin.is_(None), TarifaFlete.vigencia_fin >= fecha),
    ).order_by(
        TarifaFlete.ambito != ambito if ambito is not None else TarifaFlete.id.is_(None),
        TarifaFlete.tipo_carga.is_(None),
        TarifaFlete.vigencia_inicio.desc(),
        TarifaFlete.id.desc(),
    )
    if ambito is not None:
        stmt = stmt.where(TarifaFlete.ambito == ambito)
    row = db.execute(stmt).scalars().first()
    if row is not None:
        return row
    # Segundo intento: typo/estado en texto de viaje (ej. Vullahermosa Tab. vs Villahermosa en catalogo)
    stmt_wide = select(TarifaFlete).where(
        TarifaFlete.activo.is_(True),
        TarifaFlete.tipo_operacion == tipo_operacion,
        func.lower(func.trim(TarifaFlete.tipo_unidad)) == tu,
        tipo_carga_match,
        or_(TarifaFlete.vigencia_inicio.is_(None), TarifaFlete.vigencia_inicio <= fecha),
        or_(TarifaFlete.vigencia_fin.is_(None), TarifaFlete.vigencia_fin >= fecha),
    ).order_by(
        TarifaFlete.ambito != ambito if ambito is not None else TarifaFlete.id.is_(None),
        TarifaFlete.tipo_carga.is_(None),
        TarifaFlete.vigencia_inicio.desc(),
        TarifaFlete.id.desc(),
    )
    if ambito is not None:
        stmt_wide = stmt_wide.where(TarifaFlete.ambito == ambito)
    for cand in db.execute(stmt_wide.limit(200)).scalars().all():
        if lugares_equivalentes_para_tarifa(cand.origen, origen) and lugares_equivalentes_para_tarifa(
            cand.destino, destino
        ):
            return cand
    # Tercer intento: sin filtro SQL de tipo_unidad/tipo_carga (espacios, BD distinta, etc.)
    stmt_loose = select(TarifaFlete).where(
        TarifaFlete.activo.is_(True),
        TarifaFlete.tipo_operacion == tipo_operacion,
        or_(TarifaFlete.vigencia_inicio.is_(None), TarifaFlete.vigencia_inicio <= fecha),
        or_(TarifaFlete.vigencia_fin.is_(None), TarifaFlete.vigencia_fin >= fecha),
    ).order_by(
        TarifaFlete.ambito != ambito if ambito is not None else TarifaFlete.id.is_(None),
        TarifaFlete.tipo_carga.is_(None),
        TarifaFlete.vigencia_inicio.desc(),
        TarifaFlete.id.desc(),
    )
    if ambito is not None:
        stmt_loose = stmt_loose.where(TarifaFlete.ambito == ambito)
    req_tu = _tipo_unidad_normalizada(tipo_unidad)
    for cand in db.execute(stmt_loose.limit(400)).scalars().all():
        if _tipo_unidad_normalizada(cand.tipo_unidad) != req_tu:
            continue
        if not _fila_coincide_tipo_carga(cand, tc_norm):
            continue
        if lugares_equivalentes_para_tarifa(cand.origen, origen) and lugares_equivalentes_para_tarifa(
            cand.destino, destino
        ):
            return cand
    return None
