from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.crud import cliente as crud_cliente
from app.crud import factura as crud_factura
from app.crud import flete as crud_flete
from app.crud import orden_servicio as crud_orden_servicio
from app.models.factura import EstatusFactura
from app.schemas.factura import (
    FacturaCreate,
    FacturaGenerarDesdeFlete,
    FacturaListResponse,
    FacturaPreviewDesdeFlete,
    FacturaRead,
    FacturaUpdate,
)
from app.services.facturacion_flete import construir_factura_create, construir_preview
from app.services.audit import model_to_dict, write_audit_log

router = APIRouter()


def _factura_or_404(db: Session, factura_id: int):
    row = crud_factura.get_by_id(db, factura_id)
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Factura no encontrada.")
    return row


def _validar_fks(
    db: Session,
    *,
    cliente_id: int,
    flete_id: int | None = None,
    orden_servicio_id: int | None = None,
) -> None:
    if not crud_cliente.get_by_id(db, cliente_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Cliente no encontrado.")
    if flete_id is not None and not crud_flete.get_by_id(db, flete_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Flete no encontrado.")
    if orden_servicio_id is not None and not crud_orden_servicio.get_by_id(db, orden_servicio_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Orden de servicio no encontrada.")


@router.post("", response_model=FacturaRead, status_code=status.HTTP_201_CREATED, summary="Crear factura")
def crear_factura(payload: FacturaCreate, request: Request, db: Session = Depends(get_db)) -> FacturaRead:
    _validar_fks(
        db,
        cliente_id=payload.cliente_id,
        flete_id=payload.flete_id,
        orden_servicio_id=payload.orden_servicio_id,
    )
    row = crud_factura.create(
        db,
        {
            **payload.model_dump(),
            "folio": crud_factura.next_folio(db),
            "estatus": payload.estatus or EstatusFactura.BORRADOR,
        },
    )
    write_audit_log(
        db,
        request,
        entity="factura",
        entity_id=row.id,
        action="create",
        after=model_to_dict(row),
    )
    return FacturaRead.model_validate(row)


@router.get(
    "/preview-desde-flete/{flete_id}",
    response_model=FacturaPreviewDesdeFlete,
    summary="Vista previa de factura desde flete (precio guardado vs tarifa vigente)",
)
def preview_factura_desde_flete(
    flete_id: int,
    db: Session = Depends(get_db),
    iva_pct: Decimal = Query(Decimal("0.16"), ge=0),
    retencion_monto: Decimal = Query(Decimal("0"), ge=0),
) -> FacturaPreviewDesdeFlete:
    try:
        return construir_preview(
            db,
            flete_id=flete_id,
            iva_pct=iva_pct,
            retencion_monto=retencion_monto,
        )
    except ValueError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e)) from e


@router.post(
    "/generar-desde-flete",
    response_model=FacturaRead,
    status_code=status.HTTP_201_CREATED,
    summary="Generar factura desde flete (captura mínima; montos desde flete o tarifa recalculada)",
)
def generar_factura_desde_flete(
    payload: FacturaGenerarDesdeFlete,
    request: Request,
    db: Session = Depends(get_db),
) -> FacturaRead:
    try:
        fecha_emision = payload.fecha_emision or date.today()
        create = construir_factura_create(
            db,
            flete_id=payload.flete_id,
            fecha_emision=fecha_emision,
            fecha_vencimiento=payload.fecha_vencimiento,
            serie=payload.serie,
            iva_pct=payload.iva_pct,
            retencion_monto=payload.retencion_monto,
            usar_precio_tarifa_recalculado=payload.usar_precio_tarifa_recalculado,
            forma_pago=payload.forma_pago,
            metodo_pago=payload.metodo_pago,
            uso_cfdi=payload.uso_cfdi,
            estatus=payload.estatus,
            timbrada=payload.timbrada,
            concepto=payload.concepto,
            referencia=payload.referencia,
            observaciones=payload.observaciones,
        )
    except ValueError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e)) from e
    _validar_fks(
        db,
        cliente_id=create.cliente_id,
        flete_id=create.flete_id,
        orden_servicio_id=create.orden_servicio_id,
    )
    row = crud_factura.create(
        db,
        {
            **create.model_dump(),
            "folio": crud_factura.next_folio(db),
            "estatus": create.estatus or EstatusFactura.BORRADOR,
        },
    )
    write_audit_log(
        db,
        request,
        entity="factura",
        entity_id=row.id,
        action="create_desde_flete",
        after=model_to_dict(row),
        meta={"flete_id": payload.flete_id},
    )
    return FacturaRead.model_validate(row)


@router.get("", response_model=FacturaListResponse, summary="Listar facturas")
def listar_facturas(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    cliente_id: int | None = None,
    estatus: EstatusFactura | None = None,
    buscar: str | None = Query(None, max_length=255),
) -> FacturaListResponse:
    items, total = crud_factura.list_facturas(
        db,
        skip=skip,
        limit=limit,
        cliente_id=cliente_id,
        estatus=estatus.value if estatus else None,
        buscar=buscar,
    )
    return FacturaListResponse(
        items=[FacturaRead.model_validate(x) for x in items],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{factura_id}", response_model=FacturaRead, summary="Obtener factura")
def obtener_factura(factura_id: int, db: Session = Depends(get_db)) -> FacturaRead:
    return FacturaRead.model_validate(_factura_or_404(db, factura_id))


@router.patch("/{factura_id}", response_model=FacturaRead, summary="Actualizar factura")
def actualizar_factura(
    factura_id: int,
    payload: FacturaUpdate,
    request: Request,
    db: Session = Depends(get_db),
) -> FacturaRead:
    row = _factura_or_404(db, factura_id)
    before = model_to_dict(row)
    dump = payload.model_dump(exclude_unset=True)
    _validar_fks(
        db,
        cliente_id=dump.get("cliente_id", row.cliente_id),
        flete_id=dump.get("flete_id", row.flete_id),
        orden_servicio_id=dump.get("orden_servicio_id", row.orden_servicio_id),
    )
    updated = crud_factura.update(db, row, payload)
    write_audit_log(
        db,
        request,
        entity="factura",
        entity_id=factura_id,
        action="update",
        before=before,
        after=model_to_dict(updated),
    )
    return FacturaRead.model_validate(updated)


@router.delete("/{factura_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar factura")
def eliminar_factura(factura_id: int, request: Request, db: Session = Depends(get_db)) -> None:
    row = _factura_or_404(db, factura_id)
    before = model_to_dict(row)
    crud_factura.delete(db, row)
    write_audit_log(
        db,
        request,
        entity="factura",
        entity_id=factura_id,
        action="delete",
        before=before,
    )
