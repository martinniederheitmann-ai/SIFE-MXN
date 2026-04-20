from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.services.audit import model_to_dict, write_audit_log
from app.crud import cliente as crud_cliente
from app.schemas.cliente import (
    ClienteCondicionComercialRead,
    ClienteCondicionComercialUpsert,
    ClienteContactoCreate,
    ClienteContactoListResponse,
    ClienteContactoRead,
    ClienteContactoUpdate,
    ClienteCreate,
    ClienteDomicilioCreate,
    ClienteDomicilioListResponse,
    ClienteDomicilioRead,
    ClienteDomicilioUpdate,
    ClienteListResponse,
    ClienteRead,
    ClienteTarifaEspecialCreate,
    ClienteTarifaEspecialListResponse,
    ClienteTarifaEspecialRead,
    ClienteTarifaEspecialUpdate,
    ClienteUpdate,
)

router = APIRouter()


def _cliente_or_404(db: Session, cliente_id: int) -> ClienteRead:
    row = crud_cliente.get_by_id(db, cliente_id)
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Cliente no encontrado.")
    return row


def _contacto_or_404(db: Session, cliente_id: int, contacto_id: int):
    row = crud_cliente.get_contacto(db, contacto_id)
    if not row or row.cliente_id != cliente_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Contacto de cliente no encontrado.")
    return row


def _domicilio_or_404(db: Session, cliente_id: int, domicilio_id: int):
    row = crud_cliente.get_domicilio(db, domicilio_id)
    if not row or row.cliente_id != cliente_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Domicilio de cliente no encontrado.")
    return row


def _tarifa_especial_or_404(db: Session, cliente_id: int, tarifa_especial_id: int):
    row = crud_cliente.get_tarifa_especial(db, tarifa_especial_id)
    if not row or row.cliente_id != cliente_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Tarifa especial de cliente no encontrada.")
    return row


@router.post("", response_model=ClienteRead, status_code=status.HTTP_201_CREATED, summary="Crear cliente")
def crear_cliente(
    payload: ClienteCreate, request: Request, db: Session = Depends(get_db)
) -> ClienteRead:
    row = crud_cliente.create(db, payload)
    write_audit_log(
        db,
        request,
        entity="cliente",
        entity_id=row.id,
        action="create",
        after=model_to_dict(row),
    )
    return ClienteRead.model_validate(row)


@router.get("", response_model=ClienteListResponse, summary="Listar clientes")
def listar_clientes(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    activo: bool | None = None,
    buscar: str | None = Query(None, max_length=255, description="Texto en razón social"),
) -> ClienteListResponse:
    items, total = crud_cliente.list_clientes(
        db, skip=skip, limit=limit, activo=activo, buscar=buscar
    )
    return ClienteListResponse(
        items=[ClienteRead.model_validate(x) for x in items],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.post(
    "/{cliente_id}/contactos",
    response_model=ClienteContactoRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear contacto de cliente",
)
def crear_contacto_cliente(
    cliente_id: int,
    payload: ClienteContactoCreate,
    request: Request,
    db: Session = Depends(get_db),
) -> ClienteContactoRead:
    _cliente_or_404(db, cliente_id)
    row = crud_cliente.create_contacto(db, cliente_id, payload)
    write_audit_log(
        db,
        request,
        entity="cliente_contacto",
        entity_id=row.id,
        action="create",
        after=model_to_dict(row),
        meta={"cliente_id": cliente_id},
    )
    return ClienteContactoRead.model_validate(row)


@router.get(
    "/{cliente_id}/contactos",
    response_model=ClienteContactoListResponse,
    summary="Listar contactos de cliente",
)
def listar_contactos_cliente(cliente_id: int, db: Session = Depends(get_db)) -> ClienteContactoListResponse:
    _cliente_or_404(db, cliente_id)
    items = crud_cliente.list_contactos(db, cliente_id)
    return ClienteContactoListResponse(
        items=[ClienteContactoRead.model_validate(x) for x in items],
        total=len(items),
    )


@router.patch(
    "/{cliente_id}/contactos/{contacto_id}",
    response_model=ClienteContactoRead,
    summary="Actualizar contacto de cliente",
)
def actualizar_contacto_cliente(
    cliente_id: int,
    contacto_id: int,
    payload: ClienteContactoUpdate,
    request: Request,
    db: Session = Depends(get_db),
) -> ClienteContactoRead:
    row = _contacto_or_404(db, cliente_id, contacto_id)
    if payload.cliente_id is not None:
        _cliente_or_404(db, payload.cliente_id)
    before = model_to_dict(row)
    row = crud_cliente.update_contacto(db, row, payload)
    write_audit_log(
        db,
        request,
        entity="cliente_contacto",
        entity_id=contacto_id,
        action="update",
        before=before,
        after=model_to_dict(row),
        meta={"cliente_id": cliente_id},
    )
    return ClienteContactoRead.model_validate(row)


@router.delete(
    "/{cliente_id}/contactos/{contacto_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar contacto de cliente",
)
def eliminar_contacto_cliente(
    cliente_id: int, contacto_id: int, request: Request, db: Session = Depends(get_db)
) -> None:
    row = _contacto_or_404(db, cliente_id, contacto_id)
    before = model_to_dict(row)
    crud_cliente.delete_contacto(db, row)
    write_audit_log(
        db,
        request,
        entity="cliente_contacto",
        entity_id=contacto_id,
        action="delete",
        before=before,
        meta={"cliente_id": cliente_id},
    )


@router.post(
    "/{cliente_id}/domicilios",
    response_model=ClienteDomicilioRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear domicilio de cliente",
)
def crear_domicilio_cliente(
    cliente_id: int,
    payload: ClienteDomicilioCreate,
    request: Request,
    db: Session = Depends(get_db),
) -> ClienteDomicilioRead:
    _cliente_or_404(db, cliente_id)
    row = crud_cliente.create_domicilio(db, cliente_id, payload)
    write_audit_log(
        db,
        request,
        entity="cliente_domicilio",
        entity_id=row.id,
        action="create",
        after=model_to_dict(row),
        meta={"cliente_id": cliente_id},
    )
    return ClienteDomicilioRead.model_validate(row)


@router.get(
    "/{cliente_id}/domicilios",
    response_model=ClienteDomicilioListResponse,
    summary="Listar domicilios de cliente",
)
def listar_domicilios_cliente(cliente_id: int, db: Session = Depends(get_db)) -> ClienteDomicilioListResponse:
    _cliente_or_404(db, cliente_id)
    items = crud_cliente.list_domicilios(db, cliente_id)
    return ClienteDomicilioListResponse(
        items=[ClienteDomicilioRead.model_validate(x) for x in items],
        total=len(items),
    )


@router.patch(
    "/{cliente_id}/domicilios/{domicilio_id}",
    response_model=ClienteDomicilioRead,
    summary="Actualizar domicilio de cliente",
)
def actualizar_domicilio_cliente(
    cliente_id: int,
    domicilio_id: int,
    payload: ClienteDomicilioUpdate,
    request: Request,
    db: Session = Depends(get_db),
) -> ClienteDomicilioRead:
    row = _domicilio_or_404(db, cliente_id, domicilio_id)
    before = model_to_dict(row)
    row = crud_cliente.update_domicilio(db, row, payload)
    write_audit_log(
        db,
        request,
        entity="cliente_domicilio",
        entity_id=domicilio_id,
        action="update",
        before=before,
        after=model_to_dict(row),
        meta={"cliente_id": cliente_id},
    )
    return ClienteDomicilioRead.model_validate(row)


@router.delete(
    "/{cliente_id}/domicilios/{domicilio_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar domicilio de cliente",
)
def eliminar_domicilio_cliente(
    cliente_id: int, domicilio_id: int, request: Request, db: Session = Depends(get_db)
) -> None:
    row = _domicilio_or_404(db, cliente_id, domicilio_id)
    before = model_to_dict(row)
    crud_cliente.delete_domicilio(db, row)
    write_audit_log(
        db,
        request,
        entity="cliente_domicilio",
        entity_id=domicilio_id,
        action="delete",
        before=before,
        meta={"cliente_id": cliente_id},
    )


@router.get(
    "/{cliente_id}/condiciones-comerciales",
    response_model=ClienteCondicionComercialRead,
    summary="Obtener condiciones comerciales de cliente",
)
def obtener_condiciones_comerciales_cliente(
    cliente_id: int, db: Session = Depends(get_db)
) -> ClienteCondicionComercialRead:
    _cliente_or_404(db, cliente_id)
    row = crud_cliente.get_condicion_comercial(db, cliente_id)
    if not row:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            "Condiciones comerciales de cliente no encontradas.",
        )
    return ClienteCondicionComercialRead.model_validate(row)


@router.put(
    "/{cliente_id}/condiciones-comerciales",
    response_model=ClienteCondicionComercialRead,
    summary="Crear o actualizar condiciones comerciales de cliente",
)
def upsert_condiciones_comerciales_cliente(
    cliente_id: int,
    payload: ClienteCondicionComercialUpsert,
    request: Request,
    db: Session = Depends(get_db),
) -> ClienteCondicionComercialRead:
    _cliente_or_404(db, cliente_id)
    prev = crud_cliente.get_condicion_comercial(db, cliente_id)
    before = model_to_dict(prev) if prev else None
    row = crud_cliente.upsert_condicion_comercial(db, cliente_id, payload)
    write_audit_log(
        db,
        request,
        entity="cliente_condicion_comercial",
        entity_id=cliente_id,
        action="upsert",
        before=before,
        after=model_to_dict(row),
    )
    return ClienteCondicionComercialRead.model_validate(row)


@router.get(
    "/{cliente_id}/tarifas-especiales",
    response_model=ClienteTarifaEspecialListResponse,
    summary="Listar tarifas especiales de cliente",
)
def listar_tarifas_especiales_cliente(
    cliente_id: int, db: Session = Depends(get_db)
) -> ClienteTarifaEspecialListResponse:
    _cliente_or_404(db, cliente_id)
    items = crud_cliente.list_tarifas_especiales(db, cliente_id)
    return ClienteTarifaEspecialListResponse(
        items=[ClienteTarifaEspecialRead.model_validate(x) for x in items],
        total=len(items),
    )


@router.post(
    "/{cliente_id}/tarifas-especiales",
    response_model=ClienteTarifaEspecialRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear tarifa especial de cliente",
)
def crear_tarifa_especial_cliente(
    cliente_id: int,
    payload: ClienteTarifaEspecialCreate,
    request: Request,
    db: Session = Depends(get_db),
) -> ClienteTarifaEspecialRead:
    _cliente_or_404(db, cliente_id)
    if not crud_cliente.tarifa_flete_exists(db, payload.tarifa_flete_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Tarifa base no encontrada.")
    row = crud_cliente.create_tarifa_especial(db, cliente_id, payload)
    write_audit_log(
        db,
        request,
        entity="cliente_tarifa_especial",
        entity_id=row.id,
        action="create",
        after=model_to_dict(row),
        meta={"cliente_id": cliente_id},
    )
    return ClienteTarifaEspecialRead.model_validate(row)


@router.get(
    "/{cliente_id}/tarifas-especiales/{tarifa_especial_id}",
    response_model=ClienteTarifaEspecialRead,
    summary="Obtener tarifa especial de cliente",
)
def obtener_tarifa_especial_cliente(
    cliente_id: int,
    tarifa_especial_id: int,
    db: Session = Depends(get_db),
) -> ClienteTarifaEspecialRead:
    return ClienteTarifaEspecialRead.model_validate(
        _tarifa_especial_or_404(db, cliente_id, tarifa_especial_id)
    )


@router.patch(
    "/{cliente_id}/tarifas-especiales/{tarifa_especial_id}",
    response_model=ClienteTarifaEspecialRead,
    summary="Actualizar tarifa especial de cliente",
)
def actualizar_tarifa_especial_cliente(
    cliente_id: int,
    tarifa_especial_id: int,
    payload: ClienteTarifaEspecialUpdate,
    request: Request,
    db: Session = Depends(get_db),
) -> ClienteTarifaEspecialRead:
    row = _tarifa_especial_or_404(db, cliente_id, tarifa_especial_id)
    if payload.tarifa_flete_id is not None and not crud_cliente.tarifa_flete_exists(
        db, payload.tarifa_flete_id
    ):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Tarifa base no encontrada.")
    before = model_to_dict(row)
    row = crud_cliente.update_tarifa_especial(db, row, payload)
    write_audit_log(
        db,
        request,
        entity="cliente_tarifa_especial",
        entity_id=tarifa_especial_id,
        action="update",
        before=before,
        after=model_to_dict(row),
        meta={"cliente_id": cliente_id},
    )
    return ClienteTarifaEspecialRead.model_validate(row)


@router.delete(
    "/{cliente_id}/tarifas-especiales/{tarifa_especial_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar tarifa especial de cliente",
)
def eliminar_tarifa_especial_cliente(
    cliente_id: int,
    tarifa_especial_id: int,
    request: Request,
    db: Session = Depends(get_db),
) -> None:
    row = _tarifa_especial_or_404(db, cliente_id, tarifa_especial_id)
    before = model_to_dict(row)
    crud_cliente.delete_tarifa_especial(db, row)
    write_audit_log(
        db,
        request,
        entity="cliente_tarifa_especial",
        entity_id=tarifa_especial_id,
        action="delete",
        before=before,
        meta={"cliente_id": cliente_id},
    )


# GET/PATCH/DELETE /{cliente_id} al final para no sombrear rutas /{cliente_id}/...
@router.get("/{cliente_id}", response_model=ClienteRead, summary="Obtener cliente")
def obtener_cliente(cliente_id: int, db: Session = Depends(get_db)) -> ClienteRead:
    return ClienteRead.model_validate(_cliente_or_404(db, cliente_id))


@router.patch("/{cliente_id}", response_model=ClienteRead, summary="Actualizar cliente")
def actualizar_cliente(
    cliente_id: int,
    payload: ClienteUpdate,
    request: Request,
    db: Session = Depends(get_db),
) -> ClienteRead:
    row = _cliente_or_404(db, cliente_id)
    before = model_to_dict(row)
    updated = crud_cliente.update(db, row, payload)
    write_audit_log(
        db,
        request,
        entity="cliente",
        entity_id=cliente_id,
        action="update",
        before=before,
        after=model_to_dict(updated),
    )
    return ClienteRead.model_validate(updated)


@router.delete("/{cliente_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar cliente")
def eliminar_cliente(cliente_id: int, request: Request, db: Session = Depends(get_db)) -> None:
    row = _cliente_or_404(db, cliente_id)
    before = model_to_dict(row)
    try:
        crud_cliente.delete(db, row)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            detail="No se puede eliminar el cliente: existen fletes u otros registros vinculados.",
        ) from None
    write_audit_log(
        db,
        request,
        entity="cliente",
        entity_id=cliente_id,
        action="delete",
        before=before,
    )
