from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.operador_laboral import OperadorLaboral
from app.schemas.operador_laboral import OperadorLaboralCreate, OperadorLaboralUpdate


def get_by_operador(db: Session, id_operador: int) -> OperadorLaboral | None:
    stmt = select(OperadorLaboral).where(OperadorLaboral.id_operador == id_operador)
    return db.execute(stmt).scalar_one_or_none()


def create_or_replace(
    db: Session, id_operador: int, data: OperadorLaboralCreate
) -> OperadorLaboral:
    existing = get_by_operador(db, id_operador)
    payload = data.model_dump()
    if existing:
        for k, v in payload.items():
            setattr(existing, k, v)
        db.add(existing)
        db.commit()
        db.refresh(existing)
        return existing
    obj = OperadorLaboral(id_operador=id_operador, **payload)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update(
    db: Session, laboral: OperadorLaboral, data: OperadorLaboralUpdate
) -> OperadorLaboral:
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(laboral, k, v)
    db.add(laboral)
    db.commit()
    db.refresh(laboral)
    return laboral


def delete(db: Session, laboral: OperadorLaboral) -> None:
    db.delete(laboral)
    db.commit()
