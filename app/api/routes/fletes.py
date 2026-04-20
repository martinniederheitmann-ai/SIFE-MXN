from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.crud import cliente as crud_cliente
from app.crud import cotizacion_flete as crud_cotizacion_flete
from app.crud import flete as crud_flete
from app.crud import tarifa_flete as crud_tarifa_flete
from app.crud import transportista as crud_transportista
from app.crud import viaje as crud_viaje
from app.models.cotizacion_flete import EstatusCotizacionFlete
from app.models.flete import EstadoFlete, MetodoCalculoFlete
from app.models.transportista import TipoTransportista
from app.models.tarifa_flete import AmbitoTarifaFlete, ModalidadCobroTarifa
from app.schemas.cotizacion_flete import (
    CotizacionFleteCambiarEstatus,
    CotizacionFleteConvertir,
    CotizacionFleteCreate,
    CotizacionFleteListResponse,
    CotizacionFleteRead,
)
from app.schemas.flete import (
    FleteCompraCotizacionRead,
    FleteCompraCotizacionRequest,
    FleteCotizacionRead,
    FleteCotizacionRequest,
    FleteCreate,
    FleteListResponse,
    FleteRead,
    FleteUpdate,
)
from app.services.cotizacion_compra import cotizar_compra_con_tarifa as cotizar_compra_svc
from app.services.cotizacion_flete import cotizar_venta_con_tarifa
from app.services.audit import model_to_dict, write_audit_log

router = APIRouter()


def _cotizacion_or_404(db: Session, cotizacion_id: int):
    row = crud_cotizacion_flete.get_by_id(db, cotizacion_id)
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Cotizacion no encontrada.")
    return row


def _cotizacion_to_payload(
    request: FleteCotizacionRequest,
    result: FleteCotizacionRead,
    *,
    folio: str,
    observaciones: str | None,
) -> dict:
    return {
        "folio": folio,
        "cliente_id": result.cliente_id,
        "tarifa_flete_id": result.tarifa_id,
        "tarifa_especial_cliente_id": result.tarifa_especial_cliente_id,
        "ambito": result.ambito,
        "modalidad_cobro": result.modalidad_cobro,
        "origen": request.origen,
        "destino": request.destino,
        "tipo_unidad": request.tipo_unidad,
        "tipo_carga": request.tipo_carga,
        "distancia_km": request.distancia_km,
        "peso_kg": request.peso_kg,
        "horas_servicio": request.horas_servicio,
        "dias_servicio": request.dias_servicio,
        "urgencia": request.urgencia,
        "retorno_vacio": request.retorno_vacio,
        "riesgo_pct_extra": request.riesgo_pct_extra,
        "recargos": request.recargos,
        "costo_base_estimado": result.costo_base_estimado,
        "subtotal_estimado": result.subtotal_estimado,
        "utilidad_aplicada": result.utilidad_aplicada,
        "riesgo_aplicado": result.riesgo_aplicado,
        "urgencia_aplicada": result.urgencia_aplicada,
        "retorno_vacio_aplicado": result.retorno_vacio_aplicado,
        "carga_especial_aplicada": result.carga_especial_aplicada,
        "descuento_cliente_aplicado": result.descuento_cliente_aplicado,
        "incremento_cliente_aplicado": result.incremento_cliente_aplicado,
        "recargo_fijo_cliente_aplicado": result.recargo_fijo_cliente_aplicado,
        "precio_venta_sugerido": result.precio_venta_sugerido,
        "moneda": result.moneda,
        "detalle_calculo": result.detalle_calculo,
        "estatus": EstatusCotizacionFlete.BORRADOR,
        "observaciones": observaciones,
    }


def _validar_fks(
    db: Session,
    *,
    cliente_id: int,
    transportista_id: int,
    viaje_id: int | None,
) -> None:
    if not crud_cliente.get_by_id(db, cliente_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Cliente no encontrado.")
    if not crud_transportista.get_by_id(db, transportista_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Transportista no encontrado.")
    if viaje_id is not None and not crud_viaje.get_by_id(db, viaje_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Viaje no encontrado.")


@router.post("", response_model=FleteRead, status_code=status.HTTP_201_CREATED, summary="Crear flete")
def crear_flete(payload: FleteCreate, request: Request, db: Session = Depends(get_db)) -> FleteRead:
    if crud_flete.get_by_codigo(db, payload.codigo_flete):
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            detail=f"Ya existe un flete con el código '{payload.codigo_flete}'.",
        )
    _validar_fks(
        db,
        cliente_id=payload.cliente_id,
        transportista_id=payload.transportista_id,
        viaje_id=payload.viaje_id,
    )
    row = crud_flete.create(db, payload)
    write_audit_log(
        db,
        request,
        entity="flete",
        entity_id=row.id,
        action="create",
        after=model_to_dict(row),
    )
    return FleteRead.model_validate(row)


@router.post("/cotizar", response_model=FleteCotizacionRead, summary="Cotizar flete con tarifa")
def cotizar_flete(payload: FleteCotizacionRequest, db: Session = Depends(get_db)) -> FleteCotizacionRead:
    return cotizar_venta_con_tarifa(db, payload)


@router.post(
    "/cotizar-compra",
    response_model=FleteCompraCotizacionRead,
    summary="Cotizar costo de compra con tarifa por transportista",
)
def cotizar_compra_flete(
    payload: FleteCompraCotizacionRequest,
    db: Session = Depends(get_db),
) -> FleteCompraCotizacionRead:
    try:
        return cotizar_compra_svc(db, payload)
    except ValueError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e)) from e


@router.post(
    "/cotizaciones",
    response_model=CotizacionFleteRead,
    status_code=status.HTTP_201_CREATED,
    summary="Guardar cotizacion de flete",
)
def guardar_cotizacion_flete(
    payload: CotizacionFleteCreate,
    request: Request,
    db: Session = Depends(get_db),
) -> CotizacionFleteRead:
    result = cotizar_venta_con_tarifa(db, payload)
    row = crud_cotizacion_flete.create(
        db,
        _cotizacion_to_payload(
            payload,
            result,
            folio=crud_cotizacion_flete.next_folio(db),
            observaciones=payload.observaciones,
        ),
    )
    write_audit_log(
        db,
        request,
        entity="cotizacion_flete",
        entity_id=row.id,
        action="create",
        after=model_to_dict(row),
    )
    return CotizacionFleteRead.model_validate(row)


@router.get(
    "/cotizaciones",
    response_model=CotizacionFleteListResponse,
    summary="Listar cotizaciones de flete",
)
def listar_cotizaciones_flete(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    cliente_id: int | None = None,
    estatus: EstatusCotizacionFlete | None = None,
) -> CotizacionFleteListResponse:
    items, total = crud_cotizacion_flete.list_cotizaciones(
        db, skip=skip, limit=limit, cliente_id=cliente_id, estatus=estatus
    )
    return CotizacionFleteListResponse(
        items=[CotizacionFleteRead.model_validate(x) for x in items],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/cotizaciones/{cotizacion_id}",
    response_model=CotizacionFleteRead,
    summary="Obtener cotizacion de flete",
)
def obtener_cotizacion_flete(
    cotizacion_id: int, db: Session = Depends(get_db)
) -> CotizacionFleteRead:
    return CotizacionFleteRead.model_validate(_cotizacion_or_404(db, cotizacion_id))


@router.post(
    "/cotizaciones/{cotizacion_id}/estatus",
    response_model=CotizacionFleteRead,
    summary="Cambiar estatus de cotizacion de flete",
)
def cambiar_estatus_cotizacion_flete(
    cotizacion_id: int,
    payload: CotizacionFleteCambiarEstatus,
    request: Request,
    db: Session = Depends(get_db),
) -> CotizacionFleteRead:
    current = _cotizacion_or_404(db, cotizacion_id)
    before = model_to_dict(current)
    row = crud_cotizacion_flete.update_status(
        db,
        current,
        estatus=payload.estatus,
        observaciones=payload.observaciones,
    )
    write_audit_log(
        db,
        request,
        entity="cotizacion_flete",
        entity_id=cotizacion_id,
        action="update",
        before=before,
        after=model_to_dict(row),
        meta={"campo": "estatus"},
    )
    return CotizacionFleteRead.model_validate(row)


@router.post(
    "/cotizaciones/{cotizacion_id}/convertir",
    response_model=FleteRead,
    summary="Convertir cotizacion en flete",
)
def convertir_cotizacion_a_flete(
    cotizacion_id: int,
    payload: CotizacionFleteConvertir,
    request: Request,
    db: Session = Depends(get_db),
) -> FleteRead:
    cotizacion = _cotizacion_or_404(db, cotizacion_id)
    before_cot = model_to_dict(cotizacion)
    if cotizacion.cliente_id is None:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "La cotizacion no tiene cliente asignado y no puede convertirse en flete.",
        )
    if cotizacion.flete_id is not None:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "La cotizacion ya fue convertida previamente.",
        )
    _validar_fks(
        db,
        cliente_id=cotizacion.cliente_id,
        transportista_id=payload.transportista_id,
        viaje_id=payload.viaje_id,
    )
    if crud_flete.get_by_codigo(db, payload.codigo_flete):
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            detail=f"Ya existe un flete con el código '{payload.codigo_flete}'.",
        )
    transp = crud_transportista.get_by_id(db, payload.transportista_id)
    tipo_op = (
        transp.tipo_transportista
        if transp is not None
        else TipoTransportista.SUBCONTRATADO
    )
    row = crud_flete.create(
        db,
        FleteCreate(
            codigo_flete=payload.codigo_flete,
            cliente_id=cotizacion.cliente_id,
            transportista_id=payload.transportista_id,
            viaje_id=payload.viaje_id,
            descripcion_carga=payload.descripcion_carga,
            peso_kg=cotizacion.peso_kg,
            volumen_m3=payload.volumen_m3,
            numero_bultos=payload.numero_bultos,
            distancia_km=cotizacion.distancia_km,
            tipo_operacion=tipo_op,
            tipo_unidad=cotizacion.tipo_unidad,
            tipo_carga=cotizacion.tipo_carga,
            monto_estimado=cotizacion.precio_venta_sugerido,
            precio_venta=cotizacion.precio_venta_sugerido,
            costo_transporte_estimado=cotizacion.costo_base_estimado,
            metodo_calculo=MetodoCalculoFlete.TARIFA,
            moneda=cotizacion.moneda,
            estado=EstadoFlete.COTIZADO,
            ambito_operacion=cotizacion.ambito,
            notas=payload.notas,
        ),
    )
    cot_updated = crud_cotizacion_flete.mark_converted(db, cotizacion, row.id)
    write_audit_log(
        db,
        request,
        entity="flete",
        entity_id=row.id,
        action="create",
        after=model_to_dict(row),
        meta={"cotizacion_id": cotizacion_id},
    )
    write_audit_log(
        db,
        request,
        entity="cotizacion_flete",
        entity_id=cotizacion_id,
        action="convertir",
        before=before_cot,
        after=model_to_dict(cot_updated),
        meta={"flete_id": row.id},
    )
    return FleteRead.model_validate(row)


@router.get("", response_model=FleteListResponse, summary="Listar fletes")
def listar_fletes(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    estado: EstadoFlete | None = None,
    cliente_id: int | None = None,
    transportista_id: int | None = None,
) -> FleteListResponse:
    items, total = crud_flete.list_fletes(
        db,
        skip=skip,
        limit=limit,
        estado=estado,
        cliente_id=cliente_id,
        transportista_id=transportista_id,
    )
    return FleteListResponse(
        items=[FleteRead.model_validate(x) for x in items],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{flete_id}", response_model=FleteRead, summary="Obtener flete")
def obtener_flete(flete_id: int, db: Session = Depends(get_db)) -> FleteRead:
    row = crud_flete.get_by_id(db, flete_id)
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Flete no encontrado.")
    return FleteRead.model_validate(row)


@router.patch("/{flete_id}", response_model=FleteRead, summary="Actualizar flete")
def actualizar_flete(
    flete_id: int, payload: FleteUpdate, request: Request, db: Session = Depends(get_db)
) -> FleteRead:
    row = crud_flete.get_by_id(db, flete_id)
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Flete no encontrado.")
    before = model_to_dict(row)
    if payload.codigo_flete is not None and payload.codigo_flete != row.codigo_flete:
        if crud_flete.get_by_codigo(db, payload.codigo_flete):
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                detail=f"Ya existe un flete con el código '{payload.codigo_flete}'.",
            )
    dump = payload.model_dump(exclude_unset=True)
    cid = dump.get("cliente_id", row.cliente_id)
    tid = dump.get("transportista_id", row.transportista_id)
    vid = dump["viaje_id"] if "viaje_id" in dump else row.viaje_id
    _validar_fks(db, cliente_id=cid, transportista_id=tid, viaje_id=vid)
    updated = crud_flete.update(db, row, payload)
    write_audit_log(
        db,
        request,
        entity="flete",
        entity_id=flete_id,
        action="update",
        before=before,
        after=model_to_dict(updated),
    )
    return FleteRead.model_validate(updated)


@router.delete("/{flete_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar flete")
def eliminar_flete(flete_id: int, request: Request, db: Session = Depends(get_db)) -> None:
    row = crud_flete.get_by_id(db, flete_id)
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Flete no encontrado.")
    before = model_to_dict(row)
    crud_flete.delete(db, row)
    write_audit_log(
        db,
        request,
        entity="flete",
        entity_id=flete_id,
        action="delete",
        before=before,
    )
