"""Generación y vista previa de facturas administrativas a partir del flete (precio + tarifas)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from app.crud import flete as crud_flete
from app.models.factura import EstatusFactura
from app.schemas.factura import FacturaCreate, FacturaPreviewDesdeFlete
from app.services.cotizacion_flete import intentar_cotizar_desde_flete


def _concepto_default(flete) -> str:
    parts = [f"Servicio de flete {flete.codigo_flete}"]
    if flete.viaje:
        parts.append(f"{flete.viaje.origen} — {flete.viaje.destino}")
    return " · ".join(parts)[:255]


def construir_preview(
    db: Session,
    *,
    flete_id: int,
    iva_pct: Decimal,
    retencion_monto: Decimal,
) -> FacturaPreviewDesdeFlete:
    flete = crud_flete.get_by_id(db, flete_id)
    if not flete:
        raise ValueError("Flete no encontrado.")

    subtotal_flete = flete.precio_venta
    recot, err = intentar_cotizar_desde_flete(db, flete)
    subtotal_tarifa = recot.precio_venta_sugerido if recot else None
    diff = (subtotal_tarifa - subtotal_flete) if subtotal_tarifa is not None else None

    subtotal_propuesto = subtotal_flete
    iva_monto = subtotal_propuesto * iva_pct
    total = subtotal_propuesto + iva_monto - retencion_monto
    iva_tarifa = total_tarifa = None
    if subtotal_tarifa is not None:
        iva_tarifa = subtotal_tarifa * iva_pct
        total_tarifa = subtotal_tarifa + iva_tarifa - retencion_monto

    obs_parts = [
        f"Precio según flete (metodo_calculo={flete.metodo_calculo.value}).",
    ]
    if recot:
        obs_parts.append(f"Tarifa vigente: {recot.nombre_tarifa} (id {recot.tarifa_id}).")
    if subtotal_tarifa is not None and diff is not None and diff != 0:
        obs_parts.append(
            f"Recálculo tarifa actual: {subtotal_tarifa} (delta vs flete: {diff})."
        )
    if err and not recot:
        obs_parts.append(f"Recálculo tarifa no disponible: {err}")

    return FacturaPreviewDesdeFlete(
        flete_id=flete.id,
        cliente_id=flete.cliente_id,
        codigo_flete=flete.codigo_flete,
        metodo_calculo_flete=flete.metodo_calculo.value,
        subtotal_desde_flete=subtotal_flete,
        subtotal_desde_tarifa_recalculado=subtotal_tarifa,
        diferencia_tarifa_vs_flete=diff,
        nombre_tarifa=recot.nombre_tarifa if recot else None,
        detalle_tarifa=recot.detalle_calculo if recot else None,
        recotizacion_disponible=recot is not None,
        observaciones_sistema=" ".join(obs_parts),
        iva_pct=iva_pct,
        retencion_monto=retencion_monto,
        iva_monto=iva_monto,
        total=total,
        iva_monto_si_precio_tarifa=iva_tarifa,
        total_si_precio_tarifa=total_tarifa,
        concepto_sugerido=_concepto_default(flete),
        referencia_sugerida=flete.codigo_flete[:120],
        moneda=flete.moneda or "MXN",
    )


def construir_factura_create(
    db: Session,
    *,
    flete_id: int,
    fecha_emision: date,
    fecha_vencimiento: date | None,
    serie: str | None,
    iva_pct: Decimal,
    retencion_monto: Decimal,
    usar_precio_tarifa_recalculado: bool,
    forma_pago: str | None,
    metodo_pago: str | None,
    uso_cfdi: str | None,
    estatus: EstatusFactura,
    timbrada: bool,
    concepto: str | None,
    referencia: str | None,
    observaciones: str | None,
) -> FacturaCreate:
    flete = crud_flete.get_by_id(db, flete_id)
    if not flete:
        raise ValueError("Flete no encontrado.")

    recot, err = intentar_cotizar_desde_flete(db, flete)
    subtotal = flete.precio_venta
    if usar_precio_tarifa_recalculado:
        if recot is None:
            raise ValueError(
                f"No se puede usar precio de tarifa recalculado: {err or 'sin cotización'}"
            )
        subtotal = recot.precio_venta_sugerido

    obs = observaciones or ""
    if recot and usar_precio_tarifa_recalculado:
        obs = f"{obs} Facturación con precio recalculado desde tarifa '{recot.nombre_tarifa}'.".strip()
    elif err:
        obs = f"{obs} ({err})".strip()

    ref = (referencia.strip() if referencia else "") or flete.codigo_flete
    return FacturaCreate(
        serie=serie,
        cliente_id=flete.cliente_id,
        flete_id=flete.id,
        orden_servicio_id=None,
        fecha_emision=fecha_emision,
        fecha_vencimiento=fecha_vencimiento,
        concepto=(concepto or _concepto_default(flete))[:255],
        referencia=ref[:120] if ref else None,
        moneda=flete.moneda or "MXN",
        subtotal=subtotal,
        iva_pct=iva_pct,
        iva_monto=None,
        retencion_monto=retencion_monto,
        total=None,
        saldo_pendiente=None,
        forma_pago=forma_pago,
        metodo_pago=metodo_pago,
        uso_cfdi=uso_cfdi,
        estatus=estatus,
        timbrada=timbrada,
        observaciones=obs or None,
    )
