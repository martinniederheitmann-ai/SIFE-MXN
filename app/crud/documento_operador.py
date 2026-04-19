from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.documento_operador import DocumentoOperador
from app.schemas.documento_operador import DocumentoOperadorCreate, DocumentoOperadorUpdate


def get_by_id(db: Session, id_documento: int, id_operador: int) -> DocumentoOperador | None:
    stmt = select(DocumentoOperador).where(
        DocumentoOperador.id_documento == id_documento,
        DocumentoOperador.id_operador == id_operador,
    )
    return db.execute(stmt).scalar_one_or_none()


def list_por_operador(db: Session, id_operador: int) -> tuple[Sequence[DocumentoOperador], int]:
    stmt = (
        select(DocumentoOperador)
        .where(DocumentoOperador.id_operador == id_operador)
        .order_by(DocumentoOperador.tipo_documento, DocumentoOperador.id_documento)
    )
    rows = db.execute(stmt).scalars().all()
    return rows, len(rows)


def create(db: Session, id_operador: int, data: DocumentoOperadorCreate) -> DocumentoOperador:
    obj = DocumentoOperador(id_operador=id_operador, **data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update(
    db: Session, doc: DocumentoOperador, data: DocumentoOperadorUpdate
) -> DocumentoOperador:
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(doc, k, v)
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


def delete(db: Session, doc: DocumentoOperador) -> None:
    db.delete(doc)
    db.commit()
