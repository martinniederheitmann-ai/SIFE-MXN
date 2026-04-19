from __future__ import annotations

from collections.abc import Sequence
from datetime import date

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.transportista import (
    Transportista,
    TransportistaContacto,
    TransportistaDocumento,
)
from app.schemas.transportista import (
    TransportistaContactoCreate,
    TransportistaContactoUpdate,
    TransportistaCreate,
    TransportistaDocumentoCreate,
    TransportistaDocumentoUpdate,
    TransportistaUpdate,
)

TRANSPORTISTA_OPTIONS = (
    selectinload(Transportista.contactos),
    selectinload(Transportista.documentos),
)


def _sync_payload(payload: dict, current: Transportista | None = None) -> dict:
    if payload.get("nombre") is None and payload.get("nombre_razon_social") is not None:
        payload["nombre"] = payload["nombre_razon_social"]
    payload.pop("nombre_razon_social", None)
    if "fecha_alta" in payload and payload.get("fecha_alta") is None and current is not None:
        payload["fecha_alta"] = current.fecha_alta
    if current is None and payload.get("fecha_alta") is None:
        payload["fecha_alta"] = date.today()
    if "telefono_general" in payload and payload.get("telefono_general") is None and "telefono" in payload:
        payload["telefono_general"] = payload.get("telefono")
    elif "telefono" in payload and payload.get("telefono") is None and "telefono_general" in payload:
        payload["telefono"] = payload.get("telefono_general")
    elif current is None:
        payload["telefono_general"] = payload.get("telefono_general") or payload.get("telefono")
        payload["telefono"] = payload.get("telefono") or payload.get("telefono_general")

    if "email_general" in payload and payload.get("email_general") is None and "email" in payload:
        payload["email_general"] = payload.get("email")
    elif "email" in payload and payload.get("email") is None and "email_general" in payload:
        payload["email"] = payload.get("email_general")
    elif current is None:
        payload["email_general"] = payload.get("email_general") or payload.get("email")
        payload["email"] = payload.get("email") or payload.get("email_general")
    return payload


def get_by_id(db: Session, transportista_id: int) -> Transportista | None:
    stmt = select(Transportista).where(Transportista.id == transportista_id).options(*TRANSPORTISTA_OPTIONS)
    return db.execute(stmt).scalar_one_or_none()


def list_transportistas(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 100,
    activo: bool | None = None,
    buscar: str | None = None,
) -> tuple[Sequence[Transportista], int]:
    stmt = select(Transportista).options(*TRANSPORTISTA_OPTIONS)
    count_stmt = select(func.count()).select_from(Transportista)

    if activo is not None:
        stmt = stmt.where(Transportista.activo == activo)
        count_stmt = count_stmt.where(Transportista.activo == activo)
    if buscar:
        pat = f"%{buscar.lower()}%"
        cond = or_(
            func.lower(Transportista.nombre).like(pat),
            func.lower(func.coalesce(Transportista.nombre_comercial, "")).like(pat),
            func.lower(func.coalesce(Transportista.rfc, "")).like(pat),
        )
        stmt = stmt.where(cond)
        count_stmt = count_stmt.where(cond)

    total = db.execute(count_stmt).scalar_one()
    stmt = stmt.order_by(Transportista.nombre.asc(), Transportista.id.asc()).offset(skip).limit(limit)
    rows = db.execute(stmt).scalars().all()
    return rows, total


def create(db: Session, data: TransportistaCreate) -> Transportista:
    obj = Transportista(**_sync_payload(data.model_dump(), None))
    db.add(obj)
    db.commit()
    db.refresh(obj)
    full = get_by_id(db, obj.id)
    assert full is not None
    return full


def update(db: Session, transportista: Transportista, data: TransportistaUpdate) -> Transportista:
    payload = _sync_payload(data.model_dump(exclude_unset=True), transportista)
    for field, value in payload.items():
        setattr(transportista, field, value)
    db.add(transportista)
    db.commit()
    db.refresh(transportista)
    full = get_by_id(db, transportista.id)
    assert full is not None
    return full


def delete(db: Session, transportista: Transportista) -> None:
    db.delete(transportista)
    db.commit()


def list_contactos(db: Session, transportista_id: int) -> list[TransportistaContacto]:
    stmt = (
        select(TransportistaContacto)
        .where(TransportistaContacto.transportista_id == transportista_id)
        .order_by(
            TransportistaContacto.principal.desc(),
            TransportistaContacto.nombre.asc(),
            TransportistaContacto.id.asc(),
        )
    )
    return db.execute(stmt).scalars().all()


def get_contacto(db: Session, contacto_id: int) -> TransportistaContacto | None:
    return db.get(TransportistaContacto, contacto_id)


def _sync_principal_contacto(db: Session, transportista_id: int) -> None:
    contactos = list_contactos(db, transportista_id)
    principales = [item for item in contactos if item.principal]
    if not principales and contactos:
        contactos[0].principal = True
    elif len(principales) > 1:
        keep_id = principales[0].id
        for item in contactos:
            item.principal = item.id == keep_id
    for item in contactos:
        db.add(item)


def create_contacto(
    db: Session, transportista_id: int, data: TransportistaContactoCreate
) -> TransportistaContacto:
    if data.principal:
        for item in list_contactos(db, transportista_id):
            item.principal = False
            db.add(item)
    obj = TransportistaContacto(transportista_id=transportista_id, **data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    _sync_principal_contacto(db, transportista_id)
    db.commit()
    db.refresh(obj)
    return obj


def update_contacto(
    db: Session, contacto: TransportistaContacto, data: TransportistaContactoUpdate
) -> TransportistaContacto:
    payload = data.model_dump(exclude_unset=True)
    if payload.get("principal") is True:
        for item in list_contactos(db, contacto.transportista_id):
            if item.id != contacto.id:
                item.principal = False
                db.add(item)
    for field, value in payload.items():
        setattr(contacto, field, value)
    db.add(contacto)
    db.commit()
    _sync_principal_contacto(db, contacto.transportista_id)
    db.commit()
    db.refresh(contacto)
    return contacto


def delete_contacto(db: Session, contacto: TransportistaContacto) -> None:
    transportista_id = contacto.transportista_id
    db.delete(contacto)
    db.commit()
    _sync_principal_contacto(db, transportista_id)
    db.commit()


def list_documentos(db: Session, transportista_id: int) -> list[TransportistaDocumento]:
    stmt = (
        select(TransportistaDocumento)
        .where(TransportistaDocumento.transportista_id == transportista_id)
        .order_by(TransportistaDocumento.fecha_vencimiento.asc(), TransportistaDocumento.id.asc())
    )
    return db.execute(stmt).scalars().all()


def get_documento(db: Session, documento_id: int) -> TransportistaDocumento | None:
    return db.get(TransportistaDocumento, documento_id)


def create_documento(
    db: Session, transportista_id: int, data: TransportistaDocumentoCreate
) -> TransportistaDocumento:
    obj = TransportistaDocumento(transportista_id=transportista_id, **data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update_documento(
    db: Session, documento: TransportistaDocumento, data: TransportistaDocumentoUpdate
) -> TransportistaDocumento:
    payload = data.model_dump(exclude_unset=True)
    for field, value in payload.items():
        setattr(documento, field, value)
    db.add(documento)
    db.commit()
    db.refresh(documento)
    return documento


def delete_documento(db: Session, documento: TransportistaDocumento) -> None:
    db.delete(documento)
    db.commit()
