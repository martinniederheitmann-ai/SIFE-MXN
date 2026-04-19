from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.crud import asignacion as crud_asignacion
from app.crud import operador as crud_operador
from app.crud import unidad as crud_unidad
from app.crud import viaje as crud_viaje
from app.schemas.asignacion import (
    AsignacionCreate,
    AsignacionListResponse,
    AsignacionRead,
    AsignacionUpdate,
)

router = APIRouter()


def _asignacion_or_404(db: Session, id_asignacion: int):
    row = crud_asignacion.get_by_id(db, id_asignacion)
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Asignacion no encontrada.")
    return row


def _validar_fks(db: Session, *, id_operador: int, id_unidad: int, id_viaje: int) -> None:
    if not crud_operador.get_by_id(db, id_operador):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Operador no encontrado.")
    if not crud_unidad.get_by_id(db, id_unidad):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Unidad no encontrada.")
    if not crud_viaje.get_by_id(db, id_viaje):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Viaje no encontrado.")


@router.post(
    "",
    response_model=AsignacionRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear asignacion",
)
def crear_asignacion(payload: AsignacionCreate, db: Session = Depends(get_db)) -> AsignacionRead:
    _validar_fks(
        db,
        id_operador=payload.id_operador,
        id_unidad=payload.id_unidad,
        id_viaje=payload.id_viaje,
    )
    return AsignacionRead.model_validate(crud_asignacion.create(db, payload))


@router.get("", response_model=AsignacionListResponse, summary="Listar asignaciones")
def listar_asignaciones(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    id_operador: int | None = None,
    id_unidad: int | None = None,
    id_viaje: int | None = None,
) -> AsignacionListResponse:
    items, total = crud_asignacion.list_asignaciones(
        db,
        skip=skip,
        limit=limit,
        id_operador=id_operador,
        id_unidad=id_unidad,
        id_viaje=id_viaje,
    )
    return AsignacionListResponse(
        items=[AsignacionRead.model_validate(x) for x in items],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{id_asignacion}", response_model=AsignacionRead, summary="Obtener asignacion")
def obtener_asignacion(id_asignacion: int, db: Session = Depends(get_db)) -> AsignacionRead:
    return AsignacionRead.model_validate(_asignacion_or_404(db, id_asignacion))


@router.patch(
    "/{id_asignacion}",
    response_model=AsignacionRead,
    summary="Actualizar asignacion",
)
def actualizar_asignacion(
    id_asignacion: int, payload: AsignacionUpdate, db: Session = Depends(get_db)
) -> AsignacionRead:
    row = _asignacion_or_404(db, id_asignacion)
    dump = payload.model_dump(exclude_unset=True)
    _validar_fks(
        db,
        id_operador=dump.get("id_operador", row.id_operador),
        id_unidad=dump.get("id_unidad", row.id_unidad),
        id_viaje=dump.get("id_viaje", row.id_viaje),
    )
    return AsignacionRead.model_validate(crud_asignacion.update(db, row, payload))


@router.delete(
    "/{id_asignacion}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar asignacion",
)
def eliminar_asignacion(id_asignacion: int, db: Session = Depends(get_db)) -> None:
    crud_asignacion.delete(db, _asignacion_or_404(db, id_asignacion))
