from collections.abc import Sequence

from datetime import datetime, timezone

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.cliente import (
    Cliente,
    ClienteCondicionComercial,
    ClienteContacto,
    ClienteDomicilio,
    ClienteTarifaEspecial,
)
from app.models.tarifa_flete import TarifaFlete
from app.schemas.cliente import (
    ClienteCondicionComercialUpsert,
    ClienteContactoCreate,
    ClienteContactoUpdate,
    ClienteCreate,
    ClienteDomicilioCreate,
    ClienteDomicilioUpdate,
    ClienteTarifaEspecialCreate,
    ClienteTarifaEspecialUpdate,
    ClienteUpdate,
)

CLIENTE_OPTIONS = (
    selectinload(Cliente.contactos),
    selectinload(Cliente.domicilios),
    selectinload(Cliente.condicion_comercial),
    selectinload(Cliente.tarifas_especiales),
)


def get_by_id(db: Session, cliente_id: int) -> Cliente | None:
    stmt = select(Cliente).where(Cliente.id == cliente_id).options(*CLIENTE_OPTIONS)
    return db.execute(stmt).scalar_one_or_none()


def list_clientes(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 100,
    activo: bool | None = None,
    buscar: str | None = None,
) -> tuple[Sequence[Cliente], int]:
    stmt = select(Cliente).options(*CLIENTE_OPTIONS)
    count_stmt = select(func.count()).select_from(Cliente)

    if activo is not None:
        stmt = stmt.where(Cliente.activo == activo)
        count_stmt = count_stmt.where(Cliente.activo == activo)
    if buscar:
        pat = f"%{buscar.lower()}%"
        cond = or_(
            func.lower(Cliente.razon_social).like(pat),
            func.lower(func.coalesce(Cliente.nombre_comercial, "")).like(pat),
            func.lower(func.coalesce(Cliente.rfc, "")).like(pat),
        )
        stmt = stmt.where(cond)
        count_stmt = count_stmt.where(cond)

    total = db.execute(count_stmt).scalar_one()
    stmt = stmt.order_by(Cliente.razon_social.asc(), Cliente.id.asc()).offset(skip).limit(limit)
    rows = db.execute(stmt).scalars().all()
    return rows, total


def create(db: Session, data: ClienteCreate) -> Cliente:
    obj = Cliente(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    full = get_by_id(db, obj.id)
    assert full is not None
    return full


def update(db: Session, cliente: Cliente, data: ClienteUpdate) -> Cliente:
    payload = data.model_dump(exclude_unset=True)
    for field, value in payload.items():
        setattr(cliente, field, value)
    db.add(cliente)
    db.commit()
    db.refresh(cliente)
    full = get_by_id(db, cliente.id)
    assert full is not None
    return full


def delete(db: Session, cliente: Cliente) -> None:
    db.delete(cliente)
    db.commit()


def list_contactos(db: Session, cliente_id: int) -> list[ClienteContacto]:
    stmt = (
        select(ClienteContacto)
        .where(ClienteContacto.cliente_id == cliente_id)
        .order_by(ClienteContacto.principal.desc(), ClienteContacto.nombre.asc(), ClienteContacto.id.asc())
    )
    return db.execute(stmt).scalars().all()


def get_contacto(db: Session, contacto_id: int) -> ClienteContacto | None:
    return db.get(ClienteContacto, contacto_id)


def _sync_principal_contacto(db: Session, cliente_id: int) -> None:
    contactos = list_contactos(db, cliente_id)
    principales = [item for item in contactos if item.principal]
    if not principales and contactos:
        contactos[0].principal = True
    elif len(principales) > 1:
        keep_id = principales[0].id
        for item in contactos:
            item.principal = item.id == keep_id
    for item in contactos:
        db.add(item)


def create_contacto(db: Session, cliente_id: int, data: ClienteContactoCreate) -> ClienteContacto:
    if data.principal:
        for item in list_contactos(db, cliente_id):
            item.principal = False
            db.add(item)
    obj = ClienteContacto(cliente_id=cliente_id, **data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    _sync_principal_contacto(db, cliente_id)
    db.commit()
    db.refresh(obj)
    return obj


def update_contacto(db: Session, contacto: ClienteContacto, data: ClienteContactoUpdate) -> ClienteContacto:
    payload = data.model_dump(exclude_unset=True)
    old_cliente_id = contacto.cliente_id
    new_cliente_id = payload.pop("cliente_id", None)

    if payload.get("principal") is True:
        for item in list_contactos(db, old_cliente_id):
            if item.id != contacto.id:
                item.principal = False
                db.add(item)
    for field, value in payload.items():
        setattr(contacto, field, value)

    cliente_changed = False
    if new_cliente_id is not None and new_cliente_id != old_cliente_id:
        contacto.cliente_id = new_cliente_id
        cliente_changed = True

    db.add(contacto)
    db.commit()
    _sync_principal_contacto(db, contacto.cliente_id)
    if cliente_changed:
        _sync_principal_contacto(db, old_cliente_id)
    db.commit()
    db.refresh(contacto)
    return contacto


def delete_contacto(db: Session, contacto: ClienteContacto) -> None:
    cliente_id = contacto.cliente_id
    db.delete(contacto)
    db.commit()
    _sync_principal_contacto(db, cliente_id)
    db.commit()


def list_domicilios(db: Session, cliente_id: int) -> list[ClienteDomicilio]:
    stmt = (
        select(ClienteDomicilio)
        .where(ClienteDomicilio.cliente_id == cliente_id)
        .order_by(ClienteDomicilio.nombre_sede.asc(), ClienteDomicilio.id.asc())
    )
    return db.execute(stmt).scalars().all()


def get_domicilio(db: Session, domicilio_id: int) -> ClienteDomicilio | None:
    return db.get(ClienteDomicilio, domicilio_id)


def create_domicilio(db: Session, cliente_id: int, data: ClienteDomicilioCreate) -> ClienteDomicilio:
    obj = ClienteDomicilio(cliente_id=cliente_id, **data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update_domicilio(db: Session, domicilio: ClienteDomicilio, data: ClienteDomicilioUpdate) -> ClienteDomicilio:
    payload = data.model_dump(exclude_unset=True)
    for field, value in payload.items():
        setattr(domicilio, field, value)
    db.add(domicilio)
    db.commit()
    db.refresh(domicilio)
    return domicilio


def delete_domicilio(db: Session, domicilio: ClienteDomicilio) -> None:
    db.delete(domicilio)
    db.commit()


def get_condicion_comercial(db: Session, cliente_id: int) -> ClienteCondicionComercial | None:
    stmt = select(ClienteCondicionComercial).where(ClienteCondicionComercial.cliente_id == cliente_id)
    return db.execute(stmt).scalar_one_or_none()


def upsert_condicion_comercial(
    db: Session, cliente_id: int, data: ClienteCondicionComercialUpsert
) -> ClienteCondicionComercial:
    row = get_condicion_comercial(db, cliente_id)
    payload = data.model_dump()
    if row is None:
        row = ClienteCondicionComercial(cliente_id=cliente_id, **payload)
    else:
        for field, value in payload.items():
            setattr(row, field, value)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def list_tarifas_especiales(db: Session, cliente_id: int) -> list[ClienteTarifaEspecial]:
    stmt = (
        select(ClienteTarifaEspecial)
        .where(ClienteTarifaEspecial.cliente_id == cliente_id)
        .order_by(ClienteTarifaEspecial.prioridad.asc(), ClienteTarifaEspecial.id.asc())
    )
    return db.execute(stmt).scalars().all()


def get_tarifa_especial(db: Session, tarifa_especial_id: int) -> ClienteTarifaEspecial | None:
    return db.get(ClienteTarifaEspecial, tarifa_especial_id)


def create_tarifa_especial(
    db: Session, cliente_id: int, data: ClienteTarifaEspecialCreate
) -> ClienteTarifaEspecial:
    obj = ClienteTarifaEspecial(cliente_id=cliente_id, **data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update_tarifa_especial(
    db: Session,
    tarifa_especial: ClienteTarifaEspecial,
    data: ClienteTarifaEspecialUpdate,
) -> ClienteTarifaEspecial:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(tarifa_especial, field, value)
    db.add(tarifa_especial)
    db.commit()
    db.refresh(tarifa_especial)
    return tarifa_especial


def delete_tarifa_especial(db: Session, tarifa_especial: ClienteTarifaEspecial) -> None:
    db.delete(tarifa_especial)
    db.commit()


def get_matching_tarifa_especial(
    db: Session, *, cliente_id: int, tarifa_flete_id: int
) -> ClienteTarifaEspecial | None:
    ahora = datetime.now(timezone.utc)
    stmt = (
        select(ClienteTarifaEspecial)
        .where(
            ClienteTarifaEspecial.cliente_id == cliente_id,
            ClienteTarifaEspecial.tarifa_flete_id == tarifa_flete_id,
            ClienteTarifaEspecial.activo.is_(True),
            or_(
                ClienteTarifaEspecial.vigencia_inicio.is_(None),
                ClienteTarifaEspecial.vigencia_inicio <= ahora,
            ),
            or_(
                ClienteTarifaEspecial.vigencia_fin.is_(None),
                ClienteTarifaEspecial.vigencia_fin >= ahora,
            ),
        )
        .order_by(ClienteTarifaEspecial.prioridad.asc(), ClienteTarifaEspecial.id.asc())
    )
    return db.execute(stmt).scalar_one_or_none()


def tarifa_flete_exists(db: Session, tarifa_flete_id: int) -> bool:
    return db.get(TarifaFlete, tarifa_flete_id) is not None
