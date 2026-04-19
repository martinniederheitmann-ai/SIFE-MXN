"""Cotización de costo de compra (tarifa por transportista)."""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy.orm import Session

from app.crud import tarifa_compra_transportista as crud_tarifa_compra_transportista
from app.crud import transportista as crud_transportista
from app.schemas.flete import FleteCompraCotizacionRead, FleteCompraCotizacionRequest
from app.services.pricing_tarifas import advertencias_auditoria_tarifa, costo_base_linea_catalogo


def cotizar_compra_con_tarifa(
    db: Session, payload: FleteCompraCotizacionRequest
) -> FleteCompraCotizacionRead:
    transportista = crud_transportista.get_by_id(db, payload.transportista_id)
    if not transportista:
        raise ValueError("Transportista no encontrado.")
    tarifa = crud_tarifa_compra_transportista.get_matching_tarifa(
        db,
        transportista_id=payload.transportista_id,
        ambito=payload.ambito,
        origen=payload.origen,
        destino=payload.destino,
        tipo_unidad=payload.tipo_unidad,
        tipo_carga=payload.tipo_carga,
        tipo_transportista=transportista.tipo_transportista,
    )
    if not tarifa:
        raise ValueError(
            "No existe una tarifa de compra activa para ese transportista con esa combinacion de origen, destino, tipo de unidad y carga."
        )

    toneladas = payload.peso_kg / Decimal("1000")
    costo_base, linea_modalidad = costo_base_linea_catalogo(
        tarifa,
        distancia_km=payload.distancia_km,
        peso_kg=payload.peso_kg,
        toneladas=toneladas,
        horas_servicio=payload.horas_servicio,
        dias_servicio=payload.dias_servicio,
    )
    advertencias = advertencias_auditoria_tarifa(
        tarifa,
        distancia_km=payload.distancia_km,
        peso_kg=payload.peso_kg,
        horas_servicio=payload.horas_servicio,
        dias_servicio=payload.dias_servicio,
    )
    subtotal = costo_base + tarifa.recargo_minimo + payload.recargos
    detalle = (
        f"{linea_modalidad} | costo_linea_base {costo_base} + "
        f"recargo minimo {tarifa.recargo_minimo} + recargos adicionales {payload.recargos} => subtotal {subtotal}"
    )
    return FleteCompraCotizacionRead(
        tarifa_id=tarifa.id,
        transportista_id=payload.transportista_id,
        nombre_tarifa=tarifa.nombre_tarifa,
        ambito=tarifa.ambito,
        modalidad_cobro=tarifa.modalidad_cobro,
        linea_modalidad=linea_modalidad,
        advertencias=advertencias,
        toneladas_estimadas=toneladas,
        costo_base_estimado=costo_base,
        subtotal_estimado=subtotal,
        recargos=tarifa.recargo_minimo + payload.recargos,
        dias_credito=tarifa.dias_credito,
        costo_compra_sugerido=subtotal,
        moneda=tarifa.moneda,
        detalle_calculo=detalle,
    )
