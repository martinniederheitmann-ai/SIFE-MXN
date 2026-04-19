from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.crud import flete as crud_flete
from app.crud import gasto_viaje as crud_gasto_viaje
from app.schemas.gasto_viaje import (
    GastoViajeCreate,
    GastoViajeListResponse,
    GastoViajeRead,
    GastoViajeUpdate,
)

router = APIRouter()


def _gasto_or_404(db: Session, gasto_id: int):
    row = crud_gasto_viaje.get_by_id(db, gasto_id)
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Gasto de viaje no encontrado.")
    return row


def _flete_or_404(db: Session, flete_id: int):
    row = crud_flete.get_by_id(db, flete_id)
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Flete no encontrado.")
    return row


def _sync_flete_cost(db: Session, flete_id: int) -> None:
    flete = _flete_or_404(db, flete_id)
    total = crud_gasto_viaje.sum_gastos_by_flete(db, flete_id)
    crud_flete.sync_real_cost_from_gastos(db, flete, total)


@router.post("", response_model=GastoViajeRead, status_code=status.HTTP_201_CREATED, summary="Crear gasto de viaje")
def crear_gasto_viaje(payload: GastoViajeCreate, db: Session = Depends(get_db)) -> GastoViajeRead:
    _flete_or_404(db, payload.flete_id)
    row = crud_gasto_viaje.create(db, payload)
    _sync_flete_cost(db, payload.flete_id)
    return GastoViajeRead.model_validate(row)


@router.get("", response_model=GastoViajeListResponse, summary="Listar gastos de viaje")
def listar_gastos_viaje(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    flete_id: int | None = None,
) -> GastoViajeListResponse:
    items, total = crud_gasto_viaje.list_gastos(db, skip=skip, limit=limit, flete_id=flete_id)
    return GastoViajeListResponse(
        items=[GastoViajeRead.model_validate(x) for x in items],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{gasto_id}", response_model=GastoViajeRead, summary="Obtener gasto de viaje")
def obtener_gasto_viaje(gasto_id: int, db: Session = Depends(get_db)) -> GastoViajeRead:
    return GastoViajeRead.model_validate(_gasto_or_404(db, gasto_id))


@router.patch("/{gasto_id}", response_model=GastoViajeRead, summary="Actualizar gasto de viaje")
def actualizar_gasto_viaje(
    gasto_id: int, payload: GastoViajeUpdate, db: Session = Depends(get_db)
) -> GastoViajeRead:
    row = _gasto_or_404(db, gasto_id)
    row = crud_gasto_viaje.update(db, row, payload)
    _sync_flete_cost(db, row.flete_id)
    return GastoViajeRead.model_validate(row)


@router.delete("/{gasto_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar gasto de viaje")
def eliminar_gasto_viaje(gasto_id: int, db: Session = Depends(get_db)) -> None:
    row = _gasto_or_404(db, gasto_id)
    flete_id = row.flete_id
    crud_gasto_viaje.delete(db, row)
    _sync_flete_cost(db, flete_id)
