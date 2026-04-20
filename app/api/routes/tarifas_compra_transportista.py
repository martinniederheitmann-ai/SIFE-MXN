from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.crud import tarifa_compra_transportista as crud_tarifa_compra
from app.crud import transportista as crud_transportista
from app.models.tarifa_flete import AmbitoTarifaFlete, ModalidadCobroTarifa
from app.models.transportista import TipoTransportista
from app.schemas.tarifa_compra_transportista import (
    TarifaCompraTransportistaCreate,
    TarifaCompraTransportistaListResponse,
    TarifaCompraTransportistaRead,
    TarifaCompraTransportistaUpdate,
)
from app.services.audit import model_to_dict, write_audit_log

router = APIRouter()


def _tarifa_or_404(db: Session, tarifa_id: int):
    row = crud_tarifa_compra.get_by_id(db, tarifa_id)
    if not row:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            "Tarifa de compra por transportista no encontrada.",
        )
    return row


def _validar_transportista(db: Session, transportista_id: int) -> None:
    if not crud_transportista.get_by_id(db, transportista_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Transportista no encontrado.")


def _validar_coherencia_tipo_transportista(
    db: Session, transportista_id: int, tipo_transportista: TipoTransportista
) -> None:
    row = crud_transportista.get_by_id(db, transportista_id)
    if row and row.tipo_transportista != tipo_transportista:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "El tipo de transportista de la tarifa debe coincidir con el tipo del transportista.",
        )


@router.post(
    "",
    response_model=TarifaCompraTransportistaRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear tarifa de compra por transportista",
)
def crear_tarifa_compra_transportista(
    payload: TarifaCompraTransportistaCreate,
    request: Request,
    db: Session = Depends(get_db),
) -> TarifaCompraTransportistaRead:
    _validar_transportista(db, payload.transportista_id)
    _validar_coherencia_tipo_transportista(db, payload.transportista_id, payload.tipo_transportista)
    row = crud_tarifa_compra.create(db, payload)
    write_audit_log(
        db,
        request,
        entity="tarifa_compra_transportista",
        entity_id=row.id,
        action="create",
        after=model_to_dict(row),
    )
    return TarifaCompraTransportistaRead.model_validate(row)


@router.get(
    "",
    response_model=TarifaCompraTransportistaListResponse,
    summary="Listar tarifas de compra por transportista",
)
def listar_tarifas_compra_transportista(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    transportista_id: int | None = None,
    activo: bool | None = None,
    ambito: AmbitoTarifaFlete | None = None,
    modalidad_cobro: ModalidadCobroTarifa | None = None,
    tipo_transportista: TipoTransportista | None = None,
    buscar: str | None = Query(None, max_length=255),
) -> TarifaCompraTransportistaListResponse:
    items, total = crud_tarifa_compra.list_tarifas(
        db,
        skip=skip,
        limit=limit,
        transportista_id=transportista_id,
        activo=activo,
        ambito=ambito,
        modalidad_cobro=modalidad_cobro,
        tipo_transportista=tipo_transportista,
        buscar=buscar,
    )
    return TarifaCompraTransportistaListResponse(
        items=[TarifaCompraTransportistaRead.model_validate(x) for x in items],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{tarifa_id}",
    response_model=TarifaCompraTransportistaRead,
    summary="Obtener tarifa de compra por transportista",
)
def obtener_tarifa_compra_transportista(
    tarifa_id: int,
    db: Session = Depends(get_db),
) -> TarifaCompraTransportistaRead:
    return TarifaCompraTransportistaRead.model_validate(_tarifa_or_404(db, tarifa_id))


@router.patch(
    "/{tarifa_id}",
    response_model=TarifaCompraTransportistaRead,
    summary="Actualizar tarifa de compra por transportista",
)
def actualizar_tarifa_compra_transportista(
    tarifa_id: int,
    payload: TarifaCompraTransportistaUpdate,
    request: Request,
    db: Session = Depends(get_db),
) -> TarifaCompraTransportistaRead:
    row = _tarifa_or_404(db, tarifa_id)
    before = model_to_dict(row)
    dump = payload.model_dump(exclude_unset=True)
    if "transportista_id" in dump and dump["transportista_id"] is not None:
        _validar_transportista(db, dump["transportista_id"])
    tid = dump.get("transportista_id", row.transportista_id)
    ttipo = dump.get("tipo_transportista", row.tipo_transportista)
    if "transportista_id" in dump or "tipo_transportista" in dump:
        _validar_coherencia_tipo_transportista(db, tid, ttipo)
    updated = crud_tarifa_compra.update(db, row, payload)
    write_audit_log(
        db,
        request,
        entity="tarifa_compra_transportista",
        entity_id=tarifa_id,
        action="update",
        before=before,
        after=model_to_dict(updated),
    )
    return TarifaCompraTransportistaRead.model_validate(updated)


@router.delete(
    "/{tarifa_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar tarifa de compra por transportista",
)
def eliminar_tarifa_compra_transportista(
    tarifa_id: int,
    request: Request,
    db: Session = Depends(get_db),
) -> None:
    row = _tarifa_or_404(db, tarifa_id)
    before = model_to_dict(row)
    crud_tarifa_compra.delete(db, row)
    write_audit_log(
        db,
        request,
        entity="tarifa_compra_transportista",
        entity_id=tarifa_id,
        action="delete",
        before=before,
    )
