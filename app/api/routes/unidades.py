from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.crud import transportista as crud_transportista
from app.crud import unidad as crud_unidad
from app.schemas.unidad import UnidadCreate, UnidadListResponse, UnidadRead, UnidadUpdate

router = APIRouter()


def _unidad_or_404(db: Session, id_unidad: int):
    row = crud_unidad.get_by_id(db, id_unidad)
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Unidad no encontrada.")
    return row


@router.post("", response_model=UnidadRead, status_code=status.HTTP_201_CREATED, summary="Crear unidad")
def crear_unidad(payload: UnidadCreate, db: Session = Depends(get_db)) -> UnidadRead:
    if crud_unidad.get_by_economico(db, payload.economico):
        raise HTTPException(status.HTTP_409_CONFLICT, "Ya existe una unidad con ese economico.")
    if payload.transportista_id is not None and not crud_transportista.get_by_id(db, payload.transportista_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Transportista no encontrado.")
    return crud_unidad.create(db, payload)


@router.get("", response_model=UnidadListResponse, summary="Listar unidades")
def listar_unidades(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    activo: bool | None = None,
    buscar: str | None = Query(None, max_length=64),
    transportista_id: int | None = None,
    tipo_propiedad: str | None = Query(None, max_length=32),
    estatus_documental: str | None = Query(None, max_length=32),
) -> UnidadListResponse:
    items, total = crud_unidad.list_unidades(
        db,
        skip=skip,
        limit=limit,
        activo=activo,
        buscar=buscar,
        transportista_id=transportista_id,
        tipo_propiedad=tipo_propiedad,
        estatus_documental=estatus_documental,
    )
    return UnidadListResponse(
        items=[UnidadRead.model_validate(x) for x in items],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{id_unidad}", response_model=UnidadRead, summary="Obtener unidad")
def obtener_unidad(id_unidad: int, db: Session = Depends(get_db)) -> UnidadRead:
    return UnidadRead.model_validate(_unidad_or_404(db, id_unidad))


@router.patch("/{id_unidad}", response_model=UnidadRead, summary="Actualizar unidad")
def actualizar_unidad(
    id_unidad: int, payload: UnidadUpdate, db: Session = Depends(get_db)
) -> UnidadRead:
    row = _unidad_or_404(db, id_unidad)
    if payload.economico is not None and payload.economico != row.economico:
        if crud_unidad.get_by_economico(db, payload.economico):
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                "Ya existe una unidad con ese economico.",
            )
    if payload.transportista_id is not None and not crud_transportista.get_by_id(db, payload.transportista_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Transportista no encontrado.")
    return crud_unidad.update(db, row, payload)


@router.delete("/{id_unidad}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar unidad")
def eliminar_unidad(id_unidad: int, db: Session = Depends(get_db)) -> None:
    row = _unidad_or_404(db, id_unidad)
    try:
        crud_unidad.delete(db, row)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "No se puede eliminar la unidad: existen asignaciones vinculadas.",
        ) from None
