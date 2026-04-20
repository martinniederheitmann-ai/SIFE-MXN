from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.crud import documento_operador as crud_documento_operador
from app.crud import incidente_operador as crud_incidente_operador
from app.crud import operador as crud_operador
from app.crud import operador_laboral as crud_operador_laboral
from app.crud import pago_operador as crud_pago_operador
from app.crud import transportista as crud_transportista
from app.models.documento_operador import (
    DocumentoOperador,
    EstatusDocumentoOperador,
    TipoDocumentoOperador,
)
from app.schemas.documento_operador import (
    DocumentoOperadorCreate,
    DocumentoOperadorListResponse,
    DocumentoOperadorRead,
    DocumentoOperadorUpdate,
)
from app.schemas.incidente_operador import (
    IncidenteOperadorCreate,
    IncidenteOperadorListResponse,
    IncidenteOperadorRead,
    IncidenteOperadorUpdate,
)
from app.schemas.operador import (
    OperadorCreate,
    OperadorCumplimientoFederalRead,
    OperadorListResponse,
    OperadorRead,
    OperadorUpdate,
)
from app.schemas.operador_laboral import (
    OperadorLaboralCreate,
    OperadorLaboralRead,
    OperadorLaboralUpdate,
)
from app.services.audit import model_to_dict, write_audit_log
from app.schemas.pago_operador import (
    PagoOperadorCreate,
    PagoOperadorListResponse,
    PagoOperadorRead,
    PagoOperadorUpdate,
)

router = APIRouter()


def _operador_or_404(db: Session, id_operador: int):
    row = crud_operador.get_by_id(db, id_operador)
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Operador no encontrado.")
    return row


def _documento_vigente_hoy(doc: DocumentoOperador, hoy: date) -> bool:
    if doc.estatus == EstatusDocumentoOperador.VENCIDO:
        return False
    if doc.fecha_vencimiento is not None and doc.fecha_vencimiento < hoy:
        return False
    return True


def _cumplimiento_federal(db: Session, id_operador: int) -> OperadorCumplimientoFederalRead:
    docs, _ = crud_documento_operador.list_por_operador(db, id_operador)
    hoy = date.today()
    licencias = {
        TipoDocumentoOperador.LICENCIA_FEDERAL_B,
        TipoDocumentoOperador.LICENCIA_FEDERAL_E,
    }
    licencia_ok = any(
        d.tipo_documento in licencias and _documento_vigente_hoy(d, hoy) for d in docs
    )
    apto_ok = any(
        d.tipo_documento == TipoDocumentoOperador.APTO_MEDICO_SCT
        and _documento_vigente_hoy(d, hoy)
        for d in docs
    )
    faltantes: list[str] = []
    if not licencia_ok:
        faltantes.append("Licencia federal tipo B o E vigente")
    if not apto_ok:
        faltantes.append("Apto medico SCT vigente")
    return OperadorCumplimientoFederalRead(
        id_operador=id_operador,
        cumple_transporte_federal=licencia_ok and apto_ok,
        licencia_federal_vigente=licencia_ok,
        apto_medico_sct_vigente=apto_ok,
        faltantes=faltantes,
    )


@router.post("", response_model=OperadorRead, status_code=status.HTTP_201_CREATED, summary="Crear operador")
def crear_operador(
    payload: OperadorCreate, request: Request, db: Session = Depends(get_db)
) -> OperadorRead:
    if crud_operador.get_by_curp(db, payload.curp):
        raise HTTPException(status.HTTP_409_CONFLICT, "Ya existe un operador con esa CURP.")
    if crud_operador.get_by_nss(db, payload.nss):
        raise HTTPException(status.HTTP_409_CONFLICT, "Ya existe un operador con ese NSS.")
    if payload.transportista_id is not None and not crud_transportista.get_by_id(db, payload.transportista_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Transportista no encontrado.")
    row = crud_operador.create(db, payload)
    write_audit_log(
        db,
        request,
        entity="operador",
        entity_id=row.id,
        action="create",
        after=model_to_dict(row),
    )
    return OperadorRead.model_validate(row)


@router.get("", response_model=OperadorListResponse, summary="Listar operadores")
def listar_operadores(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    buscar: str | None = Query(None, max_length=255),
    transportista_id: int | None = None,
) -> OperadorListResponse:
    items, total = crud_operador.list_operadores(
        db, skip=skip, limit=limit, buscar=buscar, transportista_id=transportista_id
    )
    return OperadorListResponse(
        items=[OperadorRead.model_validate(x) for x in items],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{id_operador}", response_model=OperadorRead, summary="Obtener operador")
def obtener_operador(id_operador: int, db: Session = Depends(get_db)) -> OperadorRead:
    return OperadorRead.model_validate(_operador_or_404(db, id_operador))


@router.patch("/{id_operador}", response_model=OperadorRead, summary="Actualizar operador")
def actualizar_operador(
    id_operador: int,
    payload: OperadorUpdate,
    request: Request,
    db: Session = Depends(get_db),
) -> OperadorRead:
    row = _operador_or_404(db, id_operador)
    before = model_to_dict(row)
    if payload.curp is not None and payload.curp != row.curp:
        if crud_operador.get_by_curp(db, payload.curp):
            raise HTTPException(status.HTTP_409_CONFLICT, "Ya existe un operador con esa CURP.")
    if payload.nss is not None and payload.nss != row.nss:
        if crud_operador.get_by_nss(db, payload.nss):
            raise HTTPException(status.HTTP_409_CONFLICT, "Ya existe un operador con ese NSS.")
    if payload.transportista_id is not None and not crud_transportista.get_by_id(db, payload.transportista_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Transportista no encontrado.")
    updated = crud_operador.update(db, row, payload)
    write_audit_log(
        db,
        request,
        entity="operador",
        entity_id=id_operador,
        action="update",
        before=before,
        after=model_to_dict(updated),
    )
    return OperadorRead.model_validate(updated)


@router.delete("/{id_operador}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar operador")
def eliminar_operador(id_operador: int, request: Request, db: Session = Depends(get_db)) -> None:
    row = _operador_or_404(db, id_operador)
    before = model_to_dict(row)
    try:
        crud_operador.delete(db, row)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "No se puede eliminar el operador: existen asignaciones u otros registros vinculados.",
        ) from None
    write_audit_log(
        db,
        request,
        entity="operador",
        entity_id=id_operador,
        action="delete",
        before=before,
    )


@router.get(
    "/{id_operador}/cumplimiento-federal",
    response_model=OperadorCumplimientoFederalRead,
    summary="Validar cumplimiento federal",
)
def cumplimiento_federal(id_operador: int, db: Session = Depends(get_db)) -> OperadorCumplimientoFederalRead:
    _operador_or_404(db, id_operador)
    return _cumplimiento_federal(db, id_operador)


@router.get(
    "/{id_operador}/documentos",
    response_model=DocumentoOperadorListResponse,
    summary="Listar documentos de operador",
)
def listar_documentos_operador(
    id_operador: int, db: Session = Depends(get_db)
) -> DocumentoOperadorListResponse:
    _operador_or_404(db, id_operador)
    items, total = crud_documento_operador.list_por_operador(db, id_operador)
    return DocumentoOperadorListResponse(
        items=[DocumentoOperadorRead.model_validate(x) for x in items],
        total=total,
    )


@router.post(
    "/{id_operador}/documentos",
    response_model=DocumentoOperadorRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear documento de operador",
)
def crear_documento_operador(
    id_operador: int,
    payload: DocumentoOperadorCreate,
    request: Request,
    db: Session = Depends(get_db),
) -> DocumentoOperadorRead:
    _operador_or_404(db, id_operador)
    row = crud_documento_operador.create(db, id_operador, payload)
    write_audit_log(
        db,
        request,
        entity="operador_documento",
        entity_id=row.id,
        action="create",
        after=model_to_dict(row),
        meta={"id_operador": id_operador},
    )
    return DocumentoOperadorRead.model_validate(row)


@router.get(
    "/{id_operador}/documentos/{id_documento}",
    response_model=DocumentoOperadorRead,
    summary="Obtener documento de operador",
)
def obtener_documento_operador(
    id_operador: int, id_documento: int, db: Session = Depends(get_db)
) -> DocumentoOperadorRead:
    _operador_or_404(db, id_operador)
    row = crud_documento_operador.get_by_id(db, id_documento, id_operador)
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Documento no encontrado.")
    return DocumentoOperadorRead.model_validate(row)


@router.patch(
    "/{id_operador}/documentos/{id_documento}",
    response_model=DocumentoOperadorRead,
    summary="Actualizar documento de operador",
)
def actualizar_documento_operador(
    id_operador: int,
    id_documento: int,
    payload: DocumentoOperadorUpdate,
    request: Request,
    db: Session = Depends(get_db),
) -> DocumentoOperadorRead:
    _operador_or_404(db, id_operador)
    row = crud_documento_operador.get_by_id(db, id_documento, id_operador)
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Documento no encontrado.")
    before = model_to_dict(row)
    updated = crud_documento_operador.update(db, row, payload)
    write_audit_log(
        db,
        request,
        entity="operador_documento",
        entity_id=id_documento,
        action="update",
        before=before,
        after=model_to_dict(updated),
        meta={"id_operador": id_operador},
    )
    return DocumentoOperadorRead.model_validate(updated)


@router.delete(
    "/{id_operador}/documentos/{id_documento}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar documento de operador",
)
def eliminar_documento_operador(
    id_operador: int,
    id_documento: int,
    request: Request,
    db: Session = Depends(get_db),
) -> None:
    _operador_or_404(db, id_operador)
    row = crud_documento_operador.get_by_id(db, id_documento, id_operador)
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Documento no encontrado.")
    before = model_to_dict(row)
    crud_documento_operador.delete(db, row)
    write_audit_log(
        db,
        request,
        entity="operador_documento",
        entity_id=id_documento,
        action="delete",
        before=before,
        meta={"id_operador": id_operador},
    )


@router.get(
    "/{id_operador}/laboral",
    response_model=OperadorLaboralRead,
    summary="Obtener ficha laboral de operador",
)
def obtener_laboral_operador(id_operador: int, db: Session = Depends(get_db)) -> OperadorLaboralRead:
    _operador_or_404(db, id_operador)
    row = crud_operador_laboral.get_by_operador(db, id_operador)
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Ficha laboral no encontrada.")
    return OperadorLaboralRead.model_validate(row)


@router.put(
    "/{id_operador}/laboral",
    response_model=OperadorLaboralRead,
    summary="Crear o reemplazar ficha laboral de operador",
)
def crear_reemplazar_laboral_operador(
    id_operador: int,
    payload: OperadorLaboralCreate,
    request: Request,
    db: Session = Depends(get_db),
) -> OperadorLaboralRead:
    _operador_or_404(db, id_operador)
    prev = crud_operador_laboral.get_by_operador(db, id_operador)
    before = model_to_dict(prev) if prev else None
    row = crud_operador_laboral.create_or_replace(db, id_operador, payload)
    write_audit_log(
        db,
        request,
        entity="operador_laboral",
        entity_id=id_operador,
        action="upsert",
        before=before,
        after=model_to_dict(row),
    )
    return OperadorLaboralRead.model_validate(row)


@router.patch(
    "/{id_operador}/laboral",
    response_model=OperadorLaboralRead,
    summary="Actualizar ficha laboral de operador",
)
def actualizar_laboral_operador(
    id_operador: int,
    payload: OperadorLaboralUpdate,
    request: Request,
    db: Session = Depends(get_db),
) -> OperadorLaboralRead:
    _operador_or_404(db, id_operador)
    row = crud_operador_laboral.get_by_operador(db, id_operador)
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Ficha laboral no encontrada.")
    before = model_to_dict(row)
    updated = crud_operador_laboral.update(db, row, payload)
    write_audit_log(
        db,
        request,
        entity="operador_laboral",
        entity_id=id_operador,
        action="update",
        before=before,
        after=model_to_dict(updated),
    )
    return OperadorLaboralRead.model_validate(updated)


@router.delete(
    "/{id_operador}/laboral",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar ficha laboral de operador",
)
def eliminar_laboral_operador(
    id_operador: int, request: Request, db: Session = Depends(get_db)
) -> None:
    _operador_or_404(db, id_operador)
    row = crud_operador_laboral.get_by_operador(db, id_operador)
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Ficha laboral no encontrada.")
    before = model_to_dict(row)
    crud_operador_laboral.delete(db, row)
    write_audit_log(
        db,
        request,
        entity="operador_laboral",
        entity_id=id_operador,
        action="delete",
        before=before,
    )


@router.get(
    "/{id_operador}/incidentes",
    response_model=IncidenteOperadorListResponse,
    summary="Listar incidentes de operador",
)
def listar_incidentes_operador(
    id_operador: int, db: Session = Depends(get_db)
) -> IncidenteOperadorListResponse:
    _operador_or_404(db, id_operador)
    items, total = crud_incidente_operador.list_por_operador(db, id_operador)
    return IncidenteOperadorListResponse(
        items=[IncidenteOperadorRead.model_validate(x) for x in items],
        total=total,
    )


@router.post(
    "/{id_operador}/incidentes",
    response_model=IncidenteOperadorRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear incidente de operador",
)
def crear_incidente_operador(
    id_operador: int,
    payload: IncidenteOperadorCreate,
    request: Request,
    db: Session = Depends(get_db),
) -> IncidenteOperadorRead:
    _operador_or_404(db, id_operador)
    row = crud_incidente_operador.create(db, id_operador, payload)
    write_audit_log(
        db,
        request,
        entity="operador_incidente",
        entity_id=row.id,
        action="create",
        after=model_to_dict(row),
        meta={"id_operador": id_operador},
    )
    return IncidenteOperadorRead.model_validate(row)


@router.get(
    "/{id_operador}/incidentes/{id_incidente}",
    response_model=IncidenteOperadorRead,
    summary="Obtener incidente de operador",
)
def obtener_incidente_operador(
    id_operador: int, id_incidente: int, db: Session = Depends(get_db)
) -> IncidenteOperadorRead:
    _operador_or_404(db, id_operador)
    row = crud_incidente_operador.get_by_id(db, id_incidente, id_operador)
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Incidente no encontrado.")
    return IncidenteOperadorRead.model_validate(row)


@router.patch(
    "/{id_operador}/incidentes/{id_incidente}",
    response_model=IncidenteOperadorRead,
    summary="Actualizar incidente de operador",
)
def actualizar_incidente_operador(
    id_operador: int,
    id_incidente: int,
    payload: IncidenteOperadorUpdate,
    request: Request,
    db: Session = Depends(get_db),
) -> IncidenteOperadorRead:
    _operador_or_404(db, id_operador)
    row = crud_incidente_operador.get_by_id(db, id_incidente, id_operador)
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Incidente no encontrado.")
    before = model_to_dict(row)
    updated = crud_incidente_operador.update(db, row, payload)
    write_audit_log(
        db,
        request,
        entity="operador_incidente",
        entity_id=id_incidente,
        action="update",
        before=before,
        after=model_to_dict(updated),
        meta={"id_operador": id_operador},
    )
    return IncidenteOperadorRead.model_validate(updated)


@router.delete(
    "/{id_operador}/incidentes/{id_incidente}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar incidente de operador",
)
def eliminar_incidente_operador(
    id_operador: int,
    id_incidente: int,
    request: Request,
    db: Session = Depends(get_db),
) -> None:
    _operador_or_404(db, id_operador)
    row = crud_incidente_operador.get_by_id(db, id_incidente, id_operador)
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Incidente no encontrado.")
    before = model_to_dict(row)
    crud_incidente_operador.delete(db, row)
    write_audit_log(
        db,
        request,
        entity="operador_incidente",
        entity_id=id_incidente,
        action="delete",
        before=before,
        meta={"id_operador": id_operador},
    )


@router.get(
    "/{id_operador}/pagos",
    response_model=PagoOperadorListResponse,
    summary="Listar pagos de operador",
)
def listar_pagos_operador(
    id_operador: int, db: Session = Depends(get_db)
) -> PagoOperadorListResponse:
    _operador_or_404(db, id_operador)
    items, total = crud_pago_operador.list_por_operador(db, id_operador)
    return PagoOperadorListResponse(
        items=[PagoOperadorRead.model_validate(x) for x in items],
        total=total,
    )


@router.post(
    "/{id_operador}/pagos",
    response_model=PagoOperadorRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear pago de operador",
)
def crear_pago_operador(
    id_operador: int,
    payload: PagoOperadorCreate,
    request: Request,
    db: Session = Depends(get_db),
) -> PagoOperadorRead:
    _operador_or_404(db, id_operador)
    row = crud_pago_operador.create(db, id_operador, payload)
    write_audit_log(
        db,
        request,
        entity="operador_pago",
        entity_id=row.id,
        action="create",
        after=model_to_dict(row),
        meta={"id_operador": id_operador},
    )
    return PagoOperadorRead.model_validate(row)


@router.get(
    "/{id_operador}/pagos/{id_pago}",
    response_model=PagoOperadorRead,
    summary="Obtener pago de operador",
)
def obtener_pago_operador(
    id_operador: int, id_pago: int, db: Session = Depends(get_db)
) -> PagoOperadorRead:
    _operador_or_404(db, id_operador)
    row = crud_pago_operador.get_by_id(db, id_pago, id_operador)
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Pago no encontrado.")
    return PagoOperadorRead.model_validate(row)


@router.patch(
    "/{id_operador}/pagos/{id_pago}",
    response_model=PagoOperadorRead,
    summary="Actualizar pago de operador",
)
def actualizar_pago_operador(
    id_operador: int,
    id_pago: int,
    payload: PagoOperadorUpdate,
    request: Request,
    db: Session = Depends(get_db),
) -> PagoOperadorRead:
    _operador_or_404(db, id_operador)
    row = crud_pago_operador.get_by_id(db, id_pago, id_operador)
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Pago no encontrado.")
    before = model_to_dict(row)
    updated = crud_pago_operador.update(db, row, payload)
    write_audit_log(
        db,
        request,
        entity="operador_pago",
        entity_id=id_pago,
        action="update",
        before=before,
        after=model_to_dict(updated),
        meta={"id_operador": id_operador},
    )
    return PagoOperadorRead.model_validate(updated)


@router.delete(
    "/{id_operador}/pagos/{id_pago}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar pago de operador",
)
def eliminar_pago_operador(
    id_operador: int, id_pago: int, request: Request, db: Session = Depends(get_db)
) -> None:
    _operador_or_404(db, id_operador)
    row = crud_pago_operador.get_by_id(db, id_pago, id_operador)
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Pago no encontrado.")
    before = model_to_dict(row)
    crud_pago_operador.delete(db, row)
    write_audit_log(
        db,
        request,
        entity="operador_pago",
        entity_id=id_pago,
        action="delete",
        before=before,
        meta={"id_operador": id_operador},
    )
