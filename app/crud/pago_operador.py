from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.pago_operador import PagoOperador
from app.schemas.pago_operador import PagoOperadorCreate, PagoOperadorUpdate


def get_by_id(db: Session, id_pago: int, id_operador: int) -> PagoOperador | None:
    stmt = select(PagoOperador).where(
        PagoOperador.id_pago == id_pago,
        PagoOperador.id_operador == id_operador,
    )
    return db.execute(stmt).scalar_one_or_none()


def list_por_operador(db: Session, id_operador: int) -> tuple[Sequence[PagoOperador], int]:
    stmt = (
        select(PagoOperador)
        .where(PagoOperador.id_operador == id_operador)
        .order_by(PagoOperador.fecha.desc(), PagoOperador.id_pago.desc())
    )
    rows = db.execute(stmt).scalars().all()
    return rows, len(rows)


def create(db: Session, id_operador: int, data: PagoOperadorCreate) -> PagoOperador:
    obj = PagoOperador(id_operador=id_operador, **data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update(db: Session, row: PagoOperador, data: PagoOperadorUpdate) -> PagoOperador:
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(row, k, v)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def delete(db: Session, row: PagoOperador) -> None:
    db.delete(row)
    db.commit()
