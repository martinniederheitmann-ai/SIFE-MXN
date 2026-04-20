from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.crud import tarifa_flete as crud_tarifa_flete
from app.models.tarifa_flete import AmbitoTarifaFlete, ModalidadCobroTarifa
from app.models.transportista import TipoTransportista
from app.schemas.tarifa_flete import (
    TarifaFleteCreate,
    TarifaFleteListResponse,
    TarifaFleteRead,
    TarifaFleteUpdate,
)
from app.services.audit import model_to_dict, write_audit_log

router = APIRouter()


def _tarifa_or_404(db: Session, tarifa_id: int):
    row = crud_tarifa_flete.get_by_id(db, tarifa_id)
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Tarifa de flete no encontrada.")
    return row


@router.post("", response_model=TarifaFleteRead, status_code=status.HTTP_201_CREATED, summary="Crear tarifa de flete")
def crear_tarifa_flete(
    payload: TarifaFleteCreate, request: Request, db: Session = Depends(get_db)
) -> TarifaFleteRead:
    if crud_tarifa_flete.get_active_duplicate_nombre(db, payload.nombre_tarifa):
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "Este nombre de tarifa ya está en uso por otra tarifa activa. Usa otro nombre distintivo.",
        )
    row = crud_tarifa_flete.create(db, payload)
    write_audit_log(
        db,
        request,
        entity="tarifa_flete",
        entity_id=row.id,
        action="create",
        after=model_to_dict(row),
    )
    return TarifaFleteRead.model_validate(row)


@router.get("", response_model=TarifaFleteListResponse, summary="Listar tarifas de flete")
def listar_tarifas_flete(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    activo: bool | None = None,
    ambito: AmbitoTarifaFlete | None = None,
    modalidad_cobro: ModalidadCobroTarifa | None = None,
    tipo_operacion: TipoTransportista | None = None,
    buscar: str | None = Query(None, max_length=255),
) -> TarifaFleteListResponse:
    items, total = crud_tarifa_flete.list_tarifas(
        db,
        skip=skip,
        limit=limit,
        activo=activo,
        ambito=ambito,
        modalidad_cobro=modalidad_cobro,
        tipo_operacion=tipo_operacion,
        buscar=buscar,
    )
    return TarifaFleteListResponse(
        items=[TarifaFleteRead.model_validate(x) for x in items],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{tarifa_id}", response_model=TarifaFleteRead, summary="Obtener tarifa de flete")
def obtener_tarifa_flete(tarifa_id: int, db: Session = Depends(get_db)) -> TarifaFleteRead:
    return TarifaFleteRead.model_validate(_tarifa_or_404(db, tarifa_id))


@router.patch("/{tarifa_id}", response_model=TarifaFleteRead, summary="Actualizar tarifa de flete")
def actualizar_tarifa_flete(
    tarifa_id: int, payload: TarifaFleteUpdate, request: Request, db: Session = Depends(get_db)
) -> TarifaFleteRead:
    row = _tarifa_or_404(db, tarifa_id)
    before = model_to_dict(row)
    partial = payload.model_dump(exclude_unset=True)
    nombre_final = partial.get("nombre_tarifa", row.nombre_tarifa)
    activo_final = partial["activo"] if "activo" in partial else row.activo
    if activo_final and crud_tarifa_flete.get_active_duplicate_nombre(
        db, str(nombre_final), exclude_id=tarifa_id
    ):
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "Este nombre de tarifa ya está en uso por otra tarifa activa. Usa otro nombre distintivo.",
        )
    updated = crud_tarifa_flete.update(db, row, payload)
    write_audit_log(
        db,
        request,
        entity="tarifa_flete",
        entity_id=tarifa_id,
        action="update",
        before=before,
        after=model_to_dict(updated),
    )
    return TarifaFleteRead.model_validate(updated)


@router.delete("/{tarifa_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar tarifa de flete")
def eliminar_tarifa_flete(tarifa_id: int, request: Request, db: Session = Depends(get_db)) -> None:
    row = _tarifa_or_404(db, tarifa_id)
    before = model_to_dict(row)
    crud_tarifa_flete.delete(db, row)
    write_audit_log(
        db,
        request,
        entity="tarifa_flete",
        entity_id=tarifa_id,
        action="delete",
        before=before,
    )
