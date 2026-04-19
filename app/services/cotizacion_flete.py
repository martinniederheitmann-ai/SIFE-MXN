"""Cotización de venta con catálogo de tarifas (reutilizable desde rutas y facturación)."""

from __future__ import annotations

from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from sqlalchemy import func as sqlfunc, select

from app.crud import cliente as crud_cliente
from app.crud import tarifa_flete as crud_tarifa_flete
from app.models.tarifa_flete import TarifaFlete
from app.schemas.flete import FleteCotizacionRead, FleteCotizacionRequest
from app.services.pricing_tarifas import advertencias_auditoria_tarifa, costo_base_linea_catalogo


def es_carga_especial(tipo_carga: str | None) -> bool:
    if not tipo_carga:
        return False
    return tipo_carga.strip().lower() in {"refrigerada", "peligrosa"}


def cotizar_venta_con_tarifa(db: Session, payload: FleteCotizacionRequest) -> FleteCotizacionRead:
    if payload.cliente_id is not None and not crud_cliente.get_by_id(db, payload.cliente_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Cliente no encontrado.")
    tarifa = crud_tarifa_flete.get_matching_tarifa(
        db,
        ambito=payload.ambito,
        origen=payload.origen,
        destino=payload.destino,
        tipo_unidad=payload.tipo_unidad,
        tipo_carga=payload.tipo_carga,
        tipo_operacion=payload.tipo_operacion,
    )
    if not tarifa:
        n_activas = db.execute(
            select(sqlfunc.count()).select_from(TarifaFlete).where(TarifaFlete.activo.is_(True))
        ).scalar_one()
        op = payload.tipo_operacion.value
        if n_activas == 0:
            msg = (
                "No hay ninguna tarifa de flete activa en el catalogo. "
                "De de alta una tarifa (modulo Tarifas) o ejecute el script de semilla del proyecto."
            )
        else:
            msg = (
                "No existe una tarifa activa que coincida con origen/destino del viaje, tipo de operacion, "
                "tipo de unidad y tipo de carga. "
                f"Buscado: operacion={op}, origen={payload.origen!r}, destino={payload.destino!r}, "
                f"tipo_unidad={payload.tipo_unidad!r}, tipo_carga={payload.tipo_carga!r}. "
                "Revise en Tarifas de flete que exista una fila activa con esos criterios "
                "(origen y destino pueden coincidir por ciudad aunque el viaje lleve estado en el texto)."
            )
        raise HTTPException(status.HTTP_404_NOT_FOUND, msg)

    toneladas = payload.peso_kg / 1000
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
    utilidad = subtotal * tarifa.porcentaje_utilidad
    riesgo = subtotal * (tarifa.porcentaje_riesgo + payload.riesgo_pct_extra)
    urgencia = subtotal * tarifa.porcentaje_urgencia if payload.urgencia else 0
    retorno_vacio = (
        subtotal * tarifa.porcentaje_retorno_vacio if payload.retorno_vacio else 0
    )
    carga_especial = (
        subtotal * tarifa.porcentaje_carga_especial
        if es_carga_especial(payload.tipo_carga)
        else 0
    )
    precio = subtotal + utilidad + riesgo + urgencia + retorno_vacio + carga_especial
    tarifa_especial = None
    descuento_cliente = Decimal("0")
    incremento_cliente = Decimal("0")
    recargo_fijo_cliente = Decimal("0")

    if payload.cliente_id is not None:
        tarifa_especial = crud_cliente.get_matching_tarifa_especial(
            db,
            cliente_id=payload.cliente_id,
            tarifa_flete_id=tarifa.id,
        )
        if tarifa_especial is not None:
            if tarifa_especial.precio_fijo is not None:
                precio = tarifa_especial.precio_fijo + tarifa_especial.recargo_fijo
                recargo_fijo_cliente = tarifa_especial.recargo_fijo
            else:
                descuento_cliente = precio * tarifa_especial.descuento_pct
                incremento_cliente = precio * tarifa_especial.incremento_pct
                recargo_fijo_cliente = tarifa_especial.recargo_fijo
                precio = precio - descuento_cliente + incremento_cliente + recargo_fijo_cliente
    detalle = (
        f"{linea_modalidad} | costo_linea_base {costo_base} + "
        f"recargo minimo {tarifa.recargo_minimo} + recargos adicionales {payload.recargos} => subtotal {subtotal} + "
        f"utilidad {utilidad} + riesgo {riesgo} + urgencia {urgencia} + retorno {retorno_vacio} + "
        f"carga especial {carga_especial}"
    )
    if tarifa_especial is not None:
        detalle += (
            f" + acuerdo cliente '{tarifa_especial.nombre_acuerdo}'"
            f" (descuento {descuento_cliente}, incremento {incremento_cliente},"
            f" recargo fijo {recargo_fijo_cliente})"
        )
    return FleteCotizacionRead(
        tarifa_id=tarifa.id,
        nombre_tarifa=tarifa.nombre_tarifa,
        cliente_id=payload.cliente_id,
        tarifa_especial_cliente_id=tarifa_especial.id if tarifa_especial else None,
        nombre_acuerdo_cliente=tarifa_especial.nombre_acuerdo if tarifa_especial else None,
        ambito=tarifa.ambito,
        modalidad_cobro=tarifa.modalidad_cobro,
        linea_modalidad=linea_modalidad,
        advertencias=advertencias,
        toneladas_estimadas=toneladas,
        costo_base_estimado=costo_base,
        subtotal_estimado=subtotal,
        utilidad_aplicada=utilidad,
        riesgo_aplicado=riesgo,
        urgencia_aplicada=urgencia,
        retorno_vacio_aplicado=retorno_vacio,
        carga_especial_aplicada=carga_especial,
        descuento_cliente_aplicado=descuento_cliente,
        incremento_cliente_aplicado=incremento_cliente,
        recargo_fijo_cliente_aplicado=recargo_fijo_cliente,
        recargos=tarifa.recargo_minimo + payload.recargos,
        precio_venta_sugerido=precio,
        moneda=tarifa.moneda,
        detalle_calculo=detalle,
    )


def cotizacion_request_desde_flete(db: Session, flete) -> FleteCotizacionRequest | None:
    """Arma la petición de cotización a partir del flete + viaje. None si faltan datos para tarifa."""
    if not flete.viaje:
        return None
    if not flete.tipo_unidad or not str(flete.tipo_unidad).strip():
        return None
    dist = flete.distancia_km
    if dist is None and flete.viaje.kilometros_estimados is not None:
        dist = flete.viaje.kilometros_estimados
    if dist is None:
        dist = Decimal("0")
    return FleteCotizacionRequest(
        cliente_id=flete.cliente_id,
        tipo_operacion=flete.tipo_operacion,
        ambito=flete.ambito_operacion,
        origen=flete.viaje.origen,
        destino=flete.viaje.destino,
        tipo_unidad=flete.tipo_unidad.strip(),
        tipo_carga=flete.tipo_carga,
        distancia_km=dist,
        peso_kg=flete.peso_kg,
        horas_servicio=Decimal("0"),
        dias_servicio=Decimal("0"),
        urgencia=False,
        retorno_vacio=False,
        riesgo_pct_extra=Decimal("0"),
        recargos=Decimal("0"),
    )


def intentar_cotizar_desde_flete(
    db: Session, flete
) -> tuple[FleteCotizacionRead | None, str | None]:
    """
    Intenta recalcular precio con tarifas vigentes usando datos del flete/viaje.
    Devuelve (resultado, mensaje_error) donde mensaje_error explica por qué no hubo recálculo.
    """
    req = cotizacion_request_desde_flete(db, flete)
    if req is None:
        return None, "Sin viaje o sin tipo de unidad: no se puede alinear con tarifas automáticamente."
    try:
        return cotizar_venta_con_tarifa(db, req), None
    except HTTPException as e:
        return None, e.detail if isinstance(e.detail, str) else str(e.detail)
