from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.crud import transportista as crud_transportista
from app.schemas.transportista import (
    TransportistaContactoCreate,
    TransportistaContactoListResponse,
    TransportistaContactoRead,
    TransportistaContactoUpdate,
    TransportistaCreate,
    TransportistaDocumentoCreate,
    TransportistaDocumentoListResponse,
    TransportistaDocumentoRead,
    TransportistaDocumentoUpdate,
    TransportistaListResponse,
    TransportistaRead,
    TransportistaUpdate,
)

router = APIRouter()


def _transportista_or_404(db: Session, transportista_id: int):
    row = crud_transportista.get_by_id(db, transportista_id)
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Transportista no encontrado.")
    return row


def _contacto_or_404(db: Session, transportista_id: int, contacto_id: int):
    row = crud_transportista.get_contacto(db, contacto_id)
    if not row or row.transportista_id != transportista_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Contacto de transportista no encontrado.")
    return row


def _documento_or_404(db: Session, transportista_id: int, documento_id: int):
    row = crud_transportista.get_documento(db, documento_id)
    if not row or row.transportista_id != transportista_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Documento de transportista no encontrado.")
    return row


@router.post("", response_model=TransportistaRead, status_code=status.HTTP_201_CREATED, summary="Crear transportista")
def crear_transportista(
    payload: TransportistaCreate, db: Session = Depends(get_db)
) -> TransportistaRead:
    return crud_transportista.create(db, payload)


@router.get("", response_model=TransportistaListResponse, summary="Listar transportistas")
def listar_transportistas(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    activo: bool | None = None,
    buscar: str | None = Query(None, max_length=255, description="Texto en nombre"),
) -> TransportistaListResponse:
    items, total = crud_transportista.list_transportistas(
        db, skip=skip, limit=limit, activo=activo, buscar=buscar
    )
    return TransportistaListResponse(
        items=[TransportistaRead.model_validate(x) for x in items],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{transportista_id}", response_model=TransportistaRead, summary="Obtener transportista")
def obtener_transportista(
    transportista_id: int, db: Session = Depends(get_db)
) -> TransportistaRead:
    return TransportistaRead.model_validate(_transportista_or_404(db, transportista_id))


@router.patch("/{transportista_id}", response_model=TransportistaRead, summary="Actualizar transportista")
def actualizar_transportista(
    transportista_id: int, payload: TransportistaUpdate, db: Session = Depends(get_db)
) -> TransportistaRead:
    row = _transportista_or_404(db, transportista_id)
    return crud_transportista.update(db, row, payload)


@router.delete(
    "/{transportista_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar transportista"
)
def eliminar_transportista(transportista_id: int, db: Session = Depends(get_db)) -> None:
    row = _transportista_or_404(db, transportista_id)
    try:
        crud_transportista.delete(db, row)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            detail="No se puede eliminar el transportista: existen fletes u otros registros vinculados.",
        ) from None


@router.post(
    "/{transportista_id}/contactos",
    response_model=TransportistaContactoRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear contacto de transportista",
)
def crear_contacto_transportista(
    transportista_id: int,
    payload: TransportistaContactoCreate,
    db: Session = Depends(get_db),
) -> TransportistaContactoRead:
    _transportista_or_404(db, transportista_id)
    row = crud_transportista.create_contacto(db, transportista_id, payload)
    return TransportistaContactoRead.model_validate(row)


@router.get(
    "/{transportista_id}/contactos",
    response_model=TransportistaContactoListResponse,
    summary="Listar contactos de transportista",
)
def listar_contactos_transportista(
    transportista_id: int, db: Session = Depends(get_db)
) -> TransportistaContactoListResponse:
    _transportista_or_404(db, transportista_id)
    items = crud_transportista.list_contactos(db, transportista_id)
    return TransportistaContactoListResponse(
        items=[TransportistaContactoRead.model_validate(x) for x in items],
        total=len(items),
    )


@router.patch(
    "/{transportista_id}/contactos/{contacto_id}",
    response_model=TransportistaContactoRead,
    summary="Actualizar contacto de transportista",
)
def actualizar_contacto_transportista(
    transportista_id: int,
    contacto_id: int,
    payload: TransportistaContactoUpdate,
    db: Session = Depends(get_db),
) -> TransportistaContactoRead:
    row = _contacto_or_404(db, transportista_id, contacto_id)
    row = crud_transportista.update_contacto(db, row, payload)
    return TransportistaContactoRead.model_validate(row)


@router.delete(
    "/{transportista_id}/contactos/{contacto_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar contacto de transportista",
)
def eliminar_contacto_transportista(
    transportista_id: int, contacto_id: int, db: Session = Depends(get_db)
) -> None:
    row = _contacto_or_404(db, transportista_id, contacto_id)
    crud_transportista.delete_contacto(db, row)


@router.post(
    "/{transportista_id}/documentos",
    response_model=TransportistaDocumentoRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear documento de transportista",
)
def crear_documento_transportista(
    transportista_id: int,
    payload: TransportistaDocumentoCreate,
    db: Session = Depends(get_db),
) -> TransportistaDocumentoRead:
    _transportista_or_404(db, transportista_id)
    row = crud_transportista.create_documento(db, transportista_id, payload)
    return TransportistaDocumentoRead.model_validate(row)


@router.get(
    "/{transportista_id}/documentos",
    response_model=TransportistaDocumentoListResponse,
    summary="Listar documentos de transportista",
)
def listar_documentos_transportista(
    transportista_id: int, db: Session = Depends(get_db)
) -> TransportistaDocumentoListResponse:
    _transportista_or_404(db, transportista_id)
    items = crud_transportista.list_documentos(db, transportista_id)
    return TransportistaDocumentoListResponse(
        items=[TransportistaDocumentoRead.model_validate(x) for x in items],
        total=len(items),
    )


@router.patch(
    "/{transportista_id}/documentos/{documento_id}",
    response_model=TransportistaDocumentoRead,
    summary="Actualizar documento de transportista",
)
def actualizar_documento_transportista(
    transportista_id: int,
    documento_id: int,
    payload: TransportistaDocumentoUpdate,
    db: Session = Depends(get_db),
) -> TransportistaDocumentoRead:
    row = _documento_or_404(db, transportista_id, documento_id)
    row = crud_transportista.update_documento(db, row, payload)
    return TransportistaDocumentoRead.model_validate(row)


@router.delete(
    "/{transportista_id}/documentos/{documento_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar documento de transportista",
)
def eliminar_documento_transportista(
    transportista_id: int, documento_id: int, db: Session = Depends(get_db)
) -> None:
    row = _documento_or_404(db, transportista_id, documento_id)
    crud_transportista.delete_documento(db, row)
