from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models.asignacion import Asignacion
from app.models.viaje import Viaje
from app.schemas.asignacion import AsignacionCreate, AsignacionUpdate


def get_by_id(db: Session, id_asignacion: int) -> Asignacion | None:
    stmt = (
        select(Asignacion)
        .where(Asignacion.id_asignacion == id_asignacion)
        .options(
            selectinload(Asignacion.operador),
            selectinload(Asignacion.unidad),
            selectinload(Asignacion.viaje),
        )
    )
    return db.execute(stmt).scalar_one_or_none()


def list_asignaciones(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 100,
    id_operador: int | None = None,
    id_unidad: int | None = None,
    id_viaje: int | None = None,
) -> tuple[Sequence[Asignacion], int]:
    stmt = (
        select(Asignacion)
        .join(Viaje, Asignacion.id_viaje == Viaje.id)
        .options(
            selectinload(Asignacion.operador),
            selectinload(Asignacion.unidad),
            selectinload(Asignacion.viaje),
        )
    )
    count_stmt = select(func.count()).select_from(Asignacion)
    if id_operador is not None:
        stmt = stmt.where(Asignacion.id_operador == id_operador)
        count_stmt = count_stmt.where(Asignacion.id_operador == id_operador)
    if id_unidad is not None:
        stmt = stmt.where(Asignacion.id_unidad == id_unidad)
        count_stmt = count_stmt.where(Asignacion.id_unidad == id_unidad)
    if id_viaje is not None:
        stmt = stmt.where(Asignacion.id_viaje == id_viaje)
        count_stmt = count_stmt.where(Asignacion.id_viaje == id_viaje)
    total = db.execute(count_stmt).scalar_one()
    stmt = stmt.order_by(Viaje.codigo_viaje.asc(), Asignacion.id_asignacion.asc())
    stmt = stmt.offset(skip).limit(limit)
    return db.execute(stmt).scalars().all(), total


def create(db: Session, data: AsignacionCreate) -> Asignacion:
    obj = Asignacion(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    full = get_by_id(db, obj.id_asignacion)
    assert full is not None
    return full


def update(db: Session, row: Asignacion, data: AsignacionUpdate) -> Asignacion:
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(row, k, v)
    db.add(row)
    db.commit()
    db.refresh(row)
    full = get_by_id(db, row.id_asignacion)
    assert full is not None
    return full


def delete(db: Session, row: Asignacion) -> None:
    db.delete(row)
    db.commit()
