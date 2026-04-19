from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.incidente_operador import IncidenteOperador
from app.schemas.incidente_operador import IncidenteOperadorCreate, IncidenteOperadorUpdate


def get_by_id(db: Session, id_incidente: int, id_operador: int) -> IncidenteOperador | None:
    stmt = select(IncidenteOperador).where(
        IncidenteOperador.id_incidente == id_incidente,
        IncidenteOperador.id_operador == id_operador,
    )
    return db.execute(stmt).scalar_one_or_none()


def list_por_operador(db: Session, id_operador: int) -> tuple[Sequence[IncidenteOperador], int]:
    stmt = (
        select(IncidenteOperador)
        .where(IncidenteOperador.id_operador == id_operador)
        .order_by(IncidenteOperador.fecha.desc(), IncidenteOperador.id_incidente.desc())
    )
    rows = db.execute(stmt).scalars().all()
    return rows, len(rows)


def create(db: Session, id_operador: int, data: IncidenteOperadorCreate) -> IncidenteOperador:
    obj = IncidenteOperador(id_operador=id_operador, **data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update(
    db: Session, row: IncidenteOperador, data: IncidenteOperadorUpdate
) -> IncidenteOperador:
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(row, k, v)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def delete(db: Session, row: IncidenteOperador) -> None:
    db.delete(row)
    db.commit()
