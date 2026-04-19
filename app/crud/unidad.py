from collections.abc import Sequence

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.unidad import Unidad
from app.schemas.unidad import UnidadCreate, UnidadUpdate


def get_by_id(db: Session, id_unidad: int) -> Unidad | None:
    return db.get(Unidad, id_unidad)


def get_by_economico(db: Session, economico: str) -> Unidad | None:
    stmt = select(Unidad).where(Unidad.economico == economico)
    return db.execute(stmt).scalar_one_or_none()


def list_unidades(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 100,
    activo: bool | None = None,
    buscar: str | None = None,
    transportista_id: int | None = None,
    tipo_propiedad: str | None = None,
    estatus_documental: str | None = None,
) -> tuple[Sequence[Unidad], int]:
    stmt = select(Unidad)
    count_stmt = select(func.count()).select_from(Unidad)
    if activo is not None:
        stmt = stmt.where(Unidad.activo == activo)
        count_stmt = count_stmt.where(Unidad.activo == activo)
    if transportista_id is not None:
        stmt = stmt.where(Unidad.transportista_id == transportista_id)
        count_stmt = count_stmt.where(Unidad.transportista_id == transportista_id)
    if tipo_propiedad is not None and tipo_propiedad != "":
        stmt = stmt.where(Unidad.tipo_propiedad == tipo_propiedad)
        count_stmt = count_stmt.where(Unidad.tipo_propiedad == tipo_propiedad)
    if estatus_documental is not None and estatus_documental != "":
        stmt = stmt.where(Unidad.estatus_documental == estatus_documental)
        count_stmt = count_stmt.where(Unidad.estatus_documental == estatus_documental)
    if buscar:
        pat = f"%{buscar.lower()}%"
        cond = or_(
            func.lower(Unidad.economico).like(pat),
            func.lower(func.coalesce(Unidad.placas, "")).like(pat),
        )
        stmt = stmt.where(cond)
        count_stmt = count_stmt.where(cond)
    total = db.execute(count_stmt).scalar_one()
    stmt = stmt.order_by(Unidad.economico.asc(), Unidad.id_unidad.asc())
    stmt = stmt.offset(skip).limit(limit)
    return db.execute(stmt).scalars().all(), total


def create(db: Session, data: UnidadCreate) -> Unidad:
    obj = Unidad(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update(db: Session, unidad: Unidad, data: UnidadUpdate) -> Unidad:
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(unidad, k, v)
    db.add(unidad)
    db.commit()
    db.refresh(unidad)
    return unidad


def delete(db: Session, unidad: Unidad) -> None:
    db.delete(unidad)
    db.commit()
