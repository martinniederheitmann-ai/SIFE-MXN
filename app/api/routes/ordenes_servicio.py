from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.services.audit import model_to_dict, write_audit_log
from app.crud import cliente as crud_cliente
from app.crud import cotizacion_flete as crud_cotizacion_flete
from app.crud import despacho as crud_despacho
from app.crud import flete as crud_flete
from app.crud import orden_servicio as crud_orden_servicio
from app.crud import viaje as crud_viaje
from app.models.cotizacion_flete import EstatusCotizacionFlete
from app.models.orden_servicio import EstatusOrdenServicio
from app.schemas.orden_servicio import (
    OrdenServicioCambiarEstatus,
    OrdenServicioCreate,
    OrdenServicioDesdeCotizacionCreate,
    OrdenServicioListResponse,
    OrdenServicioRead,
    OrdenServicioUpdate,
)

router = APIRouter()


def _orden_or_404(db: Session, orden_id: int):
    row = crud_orden_servicio.get_by_id(db, orden_id)
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Orden de servicio no encontrada.")
    return row


def _validar_fks(
    db: Session,
    *,
    cliente_id: int,
    cotizacion_id: int | None = None,
    flete_id: int | None = None,
    viaje_id: int | None = None,
    despacho_id: int | None = None,
) -> None:
    if not crud_cliente.get_by_id(db, cliente_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Cliente no encontrado.")
    if cotizacion_id is not None and not crud_cotizacion_flete.get_by_id(db, cotizacion_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Cotizacion no encontrada.")
    if flete_id is not None and not crud_flete.get_by_id(db, flete_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Flete no encontrado.")
    if viaje_id is not None and not crud_viaje.get_by_id(db, viaje_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Viaje no encontrado.")
    if despacho_id is not None and not crud_despacho.get_by_id(db, despacho_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Despacho no encontrado.")


@router.post(
    "",
    response_model=OrdenServicioRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear orden de servicio",
)
def crear_orden_servicio(
    payload: OrdenServicioCreate, request: Request, db: Session = Depends(get_db)
) -> OrdenServicioRead:
    _validar_fks(
        db,
        cliente_id=payload.cliente_id,
        cotizacion_id=payload.cotizacion_id,
        flete_id=payload.flete_id,
        viaje_id=payload.viaje_id,
        despacho_id=payload.despacho_id,
    )
    row = crud_orden_servicio.create(
        db,
        {
            **payload.model_dump(),
            "folio": crud_orden_servicio.next_folio(db),
            "estatus": EstatusOrdenServicio.BORRADOR,
        },
    )
    write_audit_log(
        db,
        request,
        entity="orden_servicio",
        entity_id=row.id,
        action="create",
        after=model_to_dict(row),
    )
    return OrdenServicioRead.model_validate(row)


@router.post(
    "/desde-cotizacion",
    response_model=OrdenServicioRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear orden de servicio desde cotizacion",
)
def crear_orden_desde_cotizacion(
    payload: OrdenServicioDesdeCotizacionCreate,
    request: Request,
    db: Session = Depends(get_db),
) -> OrdenServicioRead:
    cotizacion = crud_cotizacion_flete.get_by_id(db, payload.cotizacion_id)
    if not cotizacion:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Cotizacion no encontrada.")
    if cotizacion.cliente_id is None:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "La cotizacion no tiene cliente asignado.",
        )
    if cotizacion.estatus not in {
        EstatusCotizacionFlete.ACEPTADA,
        EstatusCotizacionFlete.CONVERTIDA,
    }:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "La cotizacion debe estar aceptada para generar orden de servicio.",
        )
    row = crud_orden_servicio.create(
        db,
        {
            "folio": crud_orden_servicio.next_folio(db),
            "cliente_id": cotizacion.cliente_id,
            "cotizacion_id": cotizacion.id,
            "flete_id": cotizacion.flete_id,
            "viaje_id": None,
            "despacho_id": None,
            "origen": cotizacion.origen,
            "destino": cotizacion.destino,
            "tipo_unidad": cotizacion.tipo_unidad,
            "tipo_carga": cotizacion.tipo_carga,
            "peso_kg": cotizacion.peso_kg,
            "distancia_km": cotizacion.distancia_km,
            "precio_comprometido": cotizacion.precio_venta_sugerido,
            "moneda": cotizacion.moneda,
            "fecha_programada": payload.fecha_programada,
            "estatus": EstatusOrdenServicio.CONFIRMADA,
            "observaciones": payload.observaciones,
        },
    )
    write_audit_log(
        db,
        request,
        entity="orden_servicio",
        entity_id=row.id,
        action="create",
        after=model_to_dict(row),
        meta={"origen": "desde_cotizacion", "cotizacion_id": cotizacion.id},
    )
    return OrdenServicioRead.model_validate(row)


@router.get("", response_model=OrdenServicioListResponse, summary="Listar ordenes de servicio")
def listar_ordenes_servicio(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    cliente_id: int | None = None,
    estatus: EstatusOrdenServicio | None = None,
) -> OrdenServicioListResponse:
    items, total = crud_orden_servicio.list_ordenes(
        db, skip=skip, limit=limit, cliente_id=cliente_id, estatus=estatus
    )
    return OrdenServicioListResponse(
        items=[OrdenServicioRead.model_validate(x) for x in items],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{orden_id}", response_model=OrdenServicioRead, summary="Obtener orden de servicio")
def obtener_orden_servicio(orden_id: int, db: Session = Depends(get_db)) -> OrdenServicioRead:
    return OrdenServicioRead.model_validate(_orden_or_404(db, orden_id))


@router.patch("/{orden_id}", response_model=OrdenServicioRead, summary="Actualizar orden de servicio")
def actualizar_orden_servicio(
    orden_id: int,
    payload: OrdenServicioUpdate,
    request: Request,
    db: Session = Depends(get_db),
) -> OrdenServicioRead:
    row = _orden_or_404(db, orden_id)
    before = model_to_dict(row)
    dump = payload.model_dump(exclude_unset=True)
    _validar_fks(
        db,
        cliente_id=row.cliente_id,
        cotizacion_id=row.cotizacion_id,
        flete_id=dump.get("flete_id", row.flete_id),
        viaje_id=dump.get("viaje_id", row.viaje_id),
        despacho_id=dump.get("despacho_id", row.despacho_id),
    )
    row = crud_orden_servicio.update(db, row, dump)
    write_audit_log(
        db,
        request,
        entity="orden_servicio",
        entity_id=orden_id,
        action="update",
        before=before,
        after=model_to_dict(row),
    )
    return OrdenServicioRead.model_validate(row)


@router.post(
    "/{orden_id}/estatus",
    response_model=OrdenServicioRead,
    summary="Cambiar estatus de orden de servicio",
)
def cambiar_estatus_orden_servicio(
    orden_id: int,
    payload: OrdenServicioCambiarEstatus,
    request: Request,
    db: Session = Depends(get_db),
) -> OrdenServicioRead:
    current = _orden_or_404(db, orden_id)
    before = model_to_dict(current)
    row = crud_orden_servicio.change_status(
        db,
        current,
        payload.estatus,
        payload.observaciones,
    )
    write_audit_log(
        db,
        request,
        entity="orden_servicio",
        entity_id=orden_id,
        action="update",
        before=before,
        after=model_to_dict(row),
        meta={"campo": "estatus"},
    )
    return OrdenServicioRead.model_validate(row)


@router.delete(
    "/{orden_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar orden de servicio",
)
def eliminar_orden_servicio(
    orden_id: int, request: Request, db: Session = Depends(get_db)
) -> None:
    row = _orden_or_404(db, orden_id)
    before = model_to_dict(row)
    crud_orden_servicio.delete(db, row)
    write_audit_log(
        db,
        request,
        entity="orden_servicio",
        entity_id=orden_id,
        action="delete",
        before=before,
    )
