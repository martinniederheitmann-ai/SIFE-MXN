from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.crud import asignacion as crud_asignacion
from app.crud import despacho as crud_despacho
from app.crud import flete as crud_flete
from app.models.despacho import Despacho, EstadoDespacho, TipoEventoDespacho
from app.models.flete import EstadoFlete
from app.models.viaje import EstadoViaje
from app.schemas.despacho import (
    DespachoCancelar,
    DespachoCerrar,
    DespachoCreate,
    DespachoEventoCreate,
    DespachoEventoListResponse,
    DespachoEventoRead,
    DespachoListResponse,
    DespachoRead,
    DespachoRegistrarEntrega,
    DespachoRegistrarSalida,
    DespachoUpdate,
)
from app.services.cumplimiento_documental import validar_salida_por_despacho
from app.services.audit import model_to_dict, write_audit_log

router = APIRouter()


def _despacho_or_404(db: Session, id_despacho: int) -> Despacho:
    row = crud_despacho.get_by_id(db, id_despacho)
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Despacho no encontrado.")
    return row


def _validar_fks(db: Session, *, id_asignacion: int, id_flete: int | None) -> None:
    if not crud_asignacion.get_by_id(db, id_asignacion):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Asignacion no encontrada.")
    if id_flete is not None and not crud_flete.get_by_id(db, id_flete):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Flete no encontrado.")


def _sync_relations(db: Session, despacho: Despacho) -> Despacho:
    viaje = despacho.asignacion.viaje
    flete = despacho.flete

    if despacho.estatus == EstadoDespacho.PROGRAMADO:
        if flete is not None and flete.estado in {EstadoFlete.COTIZADO, EstadoFlete.CONFIRMADO}:
            flete.estado = EstadoFlete.ASIGNADO
            db.add(flete)

    if despacho.estatus in {EstadoDespacho.DESPACHADO, EstadoDespacho.EN_TRANSITO}:
        viaje.estado = EstadoViaje.EN_RUTA
        db.add(viaje)
        if flete is not None:
            flete.estado = EstadoFlete.EN_TRANSITO
            db.add(flete)

    if despacho.estatus == EstadoDespacho.ENTREGADO:
        if flete is not None:
            flete.estado = EstadoFlete.ENTREGADO
            db.add(flete)

    if despacho.estatus == EstadoDespacho.CERRADO:
        viaje.estado = EstadoViaje.COMPLETADO
        viaje.fecha_llegada_real = despacho.llegada_real or despacho.fecha_entrega
        db.add(viaje)
        if flete is not None:
            flete.estado = EstadoFlete.ENTREGADO
            db.add(flete)

    if despacho.estatus == EstadoDespacho.CANCELADO:
        viaje.estado = EstadoViaje.CANCELADO
        db.add(viaje)
        if flete is not None:
            flete.estado = EstadoFlete.CANCELADO
            db.add(flete)

    db.commit()
    refreshed = crud_despacho.get_by_id(db, despacho.id_despacho)
    assert refreshed is not None
    return refreshed


@router.post("", response_model=DespachoRead, status_code=status.HTTP_201_CREATED, summary="Crear despacho")
def crear_despacho(payload: DespachoCreate, request: Request, db: Session = Depends(get_db)) -> DespachoRead:
    if crud_despacho.get_by_asignacion(db, payload.id_asignacion):
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "Ya existe un despacho para esa asignacion.",
        )
    _validar_fks(db, id_asignacion=payload.id_asignacion, id_flete=payload.id_flete)
    row = crud_despacho.create(db, payload)
    row = _sync_relations(db, row)
    write_audit_log(
        db,
        request,
        entity="despacho",
        entity_id=row.id_despacho,
        action="create",
        after=model_to_dict(row),
    )
    return DespachoRead.model_validate(row)


@router.get("", response_model=DespachoListResponse, summary="Listar despachos")
def listar_despachos(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    estatus: EstadoDespacho | None = None,
    id_asignacion: int | None = None,
    id_flete: int | None = None,
) -> DespachoListResponse:
    items, total = crud_despacho.list_despachos(
        db,
        skip=skip,
        limit=limit,
        estatus=estatus,
        id_asignacion=id_asignacion,
        id_flete=id_flete,
    )
    return DespachoListResponse(
        items=[DespachoRead.model_validate(x) for x in items],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{id_despacho}", response_model=DespachoRead, summary="Obtener despacho")
def obtener_despacho(id_despacho: int, db: Session = Depends(get_db)) -> DespachoRead:
    return DespachoRead.model_validate(_despacho_or_404(db, id_despacho))


@router.patch("/{id_despacho}", response_model=DespachoRead, summary="Actualizar despacho")
def actualizar_despacho(
    id_despacho: int, payload: DespachoUpdate, request: Request, db: Session = Depends(get_db)
) -> DespachoRead:
    row = _despacho_or_404(db, id_despacho)
    before = model_to_dict(row)
    dump = payload.model_dump(exclude_unset=True)
    _validar_fks(
        db,
        id_asignacion=row.id_asignacion,
        id_flete=dump.get("id_flete", row.id_flete),
    )
    row = crud_despacho.update(db, row, payload)
    row = _sync_relations(db, row)
    write_audit_log(
        db,
        request,
        entity="despacho",
        entity_id=id_despacho,
        action="update",
        before=before,
        after=model_to_dict(row),
    )
    return DespachoRead.model_validate(row)


@router.post(
    "/{id_despacho}/salida",
    response_model=DespachoRead,
    summary="Registrar salida de despacho",
)
def registrar_salida(
    id_despacho: int,
    payload: DespachoRegistrarSalida,
    request: Request,
    db: Session = Depends(get_db),
    omitir_validacion_cumplimiento: bool = Query(
        False,
        description=(
            "Si es false, se valida el checklist documental antes de registrar la salida. "
            "Use true solo si la operación asume el riesgo y la documentación se regulará después."
        ),
    ),
) -> DespachoRead:
    before = model_to_dict(_despacho_or_404(db, id_despacho))
    if not omitir_validacion_cumplimiento:
        try:
            validacion = validar_salida_por_despacho(db, id_despacho=id_despacho)
        except ValueError as exc:
            raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc
        if not validacion.autorizado:
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "tipo": "cumplimiento_documental",
                    "mensaje": "La validación documental no autoriza la salida.",
                    "bloqueos": validacion.bloqueos,
                    "advertencias": validacion.advertencias,
                },
            )
    row = crud_despacho.registrar_salida(db, _despacho_or_404(db, id_despacho), payload)
    row = _sync_relations(db, row)
    crud_despacho.create_evento(
        db,
        row.id_despacho,
        DespachoEventoCreate(
            tipo_evento=TipoEventoDespacho.SALIDA,
            fecha_evento=payload.salida_real,
            descripcion=payload.observaciones_salida or "Salida registrada.",
        ),
    )
    refreshed = _despacho_or_404(db, id_despacho)
    write_audit_log(
        db,
        request,
        entity="despacho",
        entity_id=id_despacho,
        action="registrar_salida",
        before=before,
        after=model_to_dict(refreshed),
    )
    return DespachoRead.model_validate(refreshed)


@router.get(
    "/{id_despacho}/eventos",
    response_model=DespachoEventoListResponse,
    summary="Listar eventos de despacho",
)
def listar_eventos_despacho(
    id_despacho: int, db: Session = Depends(get_db)
) -> DespachoEventoListResponse:
    _despacho_or_404(db, id_despacho)
    items, total = crud_despacho.list_eventos(db, id_despacho)
    return DespachoEventoListResponse(
        items=[DespachoEventoRead.model_validate(x) for x in items],
        total=total,
    )


@router.post(
    "/{id_despacho}/eventos",
    response_model=DespachoEventoRead,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar evento de despacho",
)
def crear_evento_despacho(
    id_despacho: int, payload: DespachoEventoCreate, db: Session = Depends(get_db)
) -> DespachoEventoRead:
    row = _despacho_or_404(db, id_despacho)
    if payload.tipo_evento in {TipoEventoDespacho.CHECKPOINT, TipoEventoDespacho.INCIDENCIA} and row.estatus in {
        EstadoDespacho.PROGRAMADO,
        EstadoDespacho.DESPACHADO,
    }:
        row = crud_despacho.update(
            db,
            row,
            DespachoUpdate(estatus=EstadoDespacho.EN_TRANSITO),
        )
        _sync_relations(db, row)
    evento = crud_despacho.create_evento(db, id_despacho, payload)
    return DespachoEventoRead.model_validate(evento)


@router.post(
    "/{id_despacho}/entrega",
    response_model=DespachoRead,
    summary="Registrar entrega de despacho",
)
def registrar_entrega(
    id_despacho: int, payload: DespachoRegistrarEntrega, request: Request, db: Session = Depends(get_db)
) -> DespachoRead:
    before = model_to_dict(_despacho_or_404(db, id_despacho))
    row = crud_despacho.registrar_entrega(db, _despacho_or_404(db, id_despacho), payload)
    row = _sync_relations(db, row)
    crud_despacho.create_evento(
        db,
        row.id_despacho,
        DespachoEventoCreate(
            tipo_evento=TipoEventoDespacho.ENTREGA,
            fecha_evento=payload.fecha_entrega,
            descripcion=payload.observaciones_entrega or "Entrega registrada.",
        ),
    )
    refreshed = _despacho_or_404(db, id_despacho)
    write_audit_log(
        db,
        request,
        entity="despacho",
        entity_id=id_despacho,
        action="registrar_entrega",
        before=before,
        after=model_to_dict(refreshed),
    )
    return DespachoRead.model_validate(refreshed)


@router.post(
    "/{id_despacho}/cerrar",
    response_model=DespachoRead,
    summary="Cerrar despacho",
)
def cerrar_despacho(
    id_despacho: int, payload: DespachoCerrar, request: Request, db: Session = Depends(get_db)
) -> DespachoRead:
    before = model_to_dict(_despacho_or_404(db, id_despacho))
    row = crud_despacho.cerrar(db, _despacho_or_404(db, id_despacho), payload)
    row = _sync_relations(db, row)
    crud_despacho.create_evento(
        db,
        row.id_despacho,
        DespachoEventoCreate(
            tipo_evento=TipoEventoDespacho.CIERRE,
            fecha_evento=payload.llegada_real,
            descripcion=payload.observaciones_cierre or "Despacho cerrado.",
        ),
    )
    refreshed = _despacho_or_404(db, id_despacho)
    write_audit_log(
        db,
        request,
        entity="despacho",
        entity_id=id_despacho,
        action="cerrar",
        before=before,
        after=model_to_dict(refreshed),
    )
    return DespachoRead.model_validate(refreshed)


@router.post(
    "/{id_despacho}/cancelar",
    response_model=DespachoRead,
    summary="Cancelar despacho",
)
def cancelar_despacho(
    id_despacho: int, payload: DespachoCancelar, request: Request, db: Session = Depends(get_db)
) -> DespachoRead:
    before = model_to_dict(_despacho_or_404(db, id_despacho))
    row = crud_despacho.cancelar(
        db,
        _despacho_or_404(db, id_despacho),
        payload.motivo_cancelacion,
    )
    row = _sync_relations(db, row)
    crud_despacho.create_evento(
        db,
        row.id_despacho,
        DespachoEventoCreate(
            tipo_evento=TipoEventoDespacho.CANCELACION,
            fecha_evento=row.updated_at,
            descripcion=payload.motivo_cancelacion,
        ),
    )
    refreshed = _despacho_or_404(db, id_despacho)
    write_audit_log(
        db,
        request,
        entity="despacho",
        entity_id=id_despacho,
        action="cancelar",
        before=before,
        after=model_to_dict(refreshed),
        meta={"motivo_cancelacion": payload.motivo_cancelacion},
    )
    return DespachoRead.model_validate(refreshed)


@router.delete("/{id_despacho}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar despacho")
def eliminar_despacho(id_despacho: int, request: Request, db: Session = Depends(get_db)) -> None:
    row = _despacho_or_404(db, id_despacho)
    before = model_to_dict(row)
    crud_despacho.delete(db, row)
    write_audit_log(
        db,
        request,
        entity="despacho",
        entity_id=id_despacho,
        action="delete",
        before=before,
    )
