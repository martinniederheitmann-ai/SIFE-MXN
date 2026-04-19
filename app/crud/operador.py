from collections.abc import Sequence

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.operador import Operador
from app.schemas.operador import OperadorCreate, OperadorUpdate


def get_by_id(db: Session, id_operador: int) -> Operador | None:
    return db.get(Operador, id_operador)


def get_by_curp(db: Session, curp: str) -> Operador | None:
    stmt = select(Operador).where(Operador.curp == curp)
    return db.execute(stmt).scalar_one_or_none()


def get_by_nss(db: Session, nss: str) -> Operador | None:
    stmt = select(Operador).where(Operador.nss == nss)
    return db.execute(stmt).scalar_one_or_none()


def list_operadores(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 100,
    buscar: str | None = None,
    transportista_id: int | None = None,
) -> tuple[Sequence[Operador], int]:
    stmt = select(Operador)
    count_stmt = select(func.count()).select_from(Operador)
    if transportista_id is not None:
        stmt = stmt.where(Operador.transportista_id == transportista_id)
        count_stmt = count_stmt.where(Operador.transportista_id == transportista_id)
    if buscar:
        pat = f"%{buscar.lower()}%"
        cond = or_(
            func.lower(Operador.nombre).like(pat),
            func.lower(Operador.apellido_paterno).like(pat),
            func.lower(Operador.apellido_materno).like(pat),
            func.lower(Operador.curp).like(pat),
        )
        stmt = stmt.where(cond)
        count_stmt = count_stmt.where(cond)
    total = db.execute(count_stmt).scalar_one()
    stmt = stmt.order_by(Operador.apellido_paterno, Operador.apellido_materno, Operador.nombre)
    stmt = stmt.offset(skip).limit(limit)
    return db.execute(stmt).scalars().all(), total


def create(db: Session, data: OperadorCreate) -> Operador:
    obj = Operador(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update(db: Session, operador: Operador, data: OperadorUpdate) -> Operador:
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(operador, k, v)
    db.add(operador)
    db.commit()
    db.refresh(operador)
    return operador


def delete(db: Session, operador: Operador) -> None:
    db.delete(operador)
    db.commit()
