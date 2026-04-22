from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.crud import baja_dano as crud_bd
from app.crud import flete as crud_flete
from app.crud import operador as crud_operador
from app.crud import unidad as crud_unidad
from app.schemas.baja_dano import BajaDanoCreate, BajaDanoListResponse, BajaDanoRead, BajaDanoUpdate
from app.services.audit import model_to_dict, write_audit_log

router = APIRouter()


def _row_or_404(db: Session, row_id: int):
    row = crud_bd.get_by_id(db, row_id)
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Registro no encontrado.")
    return row


def _optional_flete(db: Session, flete_id: int | None) -> None:
    if flete_id is None:
        return
    if crud_flete.get_by_id(db, flete_id) is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Flete no encontrado.")


def _optional_unidad(db: Session, id_unidad: int | None) -> None:
    if id_unidad is None:
        return
    if crud_unidad.get_by_id(db, id_unidad) is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Unidad no encontrada.")


def _optional_operador(db: Session, id_operador: int | None) -> None:
    if id_operador is None:
        return
    if crud_operador.get_by_id(db, id_operador) is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Operador no encontrado.")


@router.post("", response_model=BajaDanoRead, status_code=status.HTTP_201_CREATED, summary="Registrar baja o daño")
def crear_registro(
    payload: BajaDanoCreate, request: Request, db: Session = Depends(get_db)
) -> BajaDanoRead:
    _optional_flete(db, payload.flete_id)
    _optional_unidad(db, payload.id_unidad)
    _optional_operador(db, payload.id_operador)
    row = crud_bd.create(db, payload)
    write_audit_log(
        db,
        request,
        entity="baja_dano",
        entity_id=row.id,
        action="create",
        after=model_to_dict(row),
    )
    return BajaDanoRead.model_validate(row)


@router.get("", response_model=BajaDanoListResponse, summary="Listar bajas y daños")
def listar(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    tipo: str | None = None,
    flete_id: int | None = None,
) -> BajaDanoListResponse:
    items, total = crud_bd.list_rows(db, skip=skip, limit=limit, tipo=tipo, flete_id=flete_id)
    return BajaDanoListResponse(
        items=[BajaDanoRead.model_validate(x) for x in items],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{row_id}", response_model=BajaDanoRead, summary="Obtener registro")
def obtener(row_id: int, db: Session = Depends(get_db)) -> BajaDanoRead:
    return BajaDanoRead.model_validate(_row_or_404(db, row_id))


@router.patch("/{row_id}", response_model=BajaDanoRead, summary="Actualizar registro")
def actualizar(
    row_id: int, payload: BajaDanoUpdate, request: Request, db: Session = Depends(get_db)
) -> BajaDanoRead:
    row = _row_or_404(db, row_id)
    before = model_to_dict(row)
    data = payload.model_dump(exclude_unset=True)
    if "flete_id" in data:
        _optional_flete(db, data.get("flete_id"))
    if "id_unidad" in data:
        _optional_unidad(db, data.get("id_unidad"))
    if "id_operador" in data:
        _optional_operador(db, data.get("id_operador"))
    row = crud_bd.update(db, row, payload)
    write_audit_log(
        db,
        request,
        entity="baja_dano",
        entity_id=row_id,
        action="update",
        before=before,
        after=model_to_dict(row),
    )
    return BajaDanoRead.model_validate(row)


@router.delete("/{row_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar registro")
def eliminar(row_id: int, request: Request, db: Session = Depends(get_db)) -> None:
    row = _row_or_404(db, row_id)
    before = model_to_dict(row)
    crud_bd.delete(db, row)
    write_audit_log(
        db,
        request,
        entity="baja_dano",
        entity_id=row_id,
        action="delete",
        before=before,
    )
