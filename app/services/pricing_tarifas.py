"""
Línea de costo base según modalidad de cobro del catálogo (venta y compra).

Antes la modalidad era solo metadato; aquí define qué componentes (base, km, peso,
hora, día) entran en el costo_base antes de recargos y márgenes (venta).
"""

from __future__ import annotations

from decimal import Decimal
from typing import Protocol

from app.models.tarifa_flete import ModalidadCobroTarifa


class _TarifaLinea(Protocol):
    modalidad_cobro: ModalidadCobroTarifa
    tarifa_base: Decimal
    tarifa_km: Decimal
    tarifa_kg: Decimal
    tarifa_tonelada: Decimal
    tarifa_hora: Decimal
    tarifa_dia: Decimal


def costo_base_linea_catalogo(
    tarifa: _TarifaLinea,
    *,
    distancia_km: Decimal,
    peso_kg: Decimal,
    toneladas: Decimal,
    horas_servicio: Decimal,
    dias_servicio: Decimal,
) -> tuple[Decimal, str]:
    """
    Costo lineal antes de recargo_minimo y recargos del pedido.
    Devuelve (importe, texto resumido del modo aplicado).
    """
    m = tarifa.modalidad_cobro
    b = tarifa.tarifa_base
    if m == ModalidadCobroTarifa.MIXTA:
        total = (
            b
            + (tarifa.tarifa_km * distancia_km)
            + (tarifa.tarifa_kg * peso_kg)
            + (tarifa.tarifa_tonelada * toneladas)
            + (tarifa.tarifa_hora * horas_servicio)
            + (tarifa.tarifa_dia * dias_servicio)
        )
        desc = (
            f"MIXTA: base {b} + km({distancia_km}×{tarifa.tarifa_km}) + "
            f"kg({peso_kg}×{tarifa.tarifa_kg}) + ton({toneladas}×{tarifa.tarifa_tonelada}) + "
            f"h({horas_servicio}×{tarifa.tarifa_hora}) + d({dias_servicio}×{tarifa.tarifa_dia})"
        )
        return total, desc
    if m == ModalidadCobroTarifa.POR_KM:
        total = b + (tarifa.tarifa_km * distancia_km)
        desc = f"POR_KM: base {b} + km({distancia_km}×{tarifa.tarifa_km})"
        return total, desc
    if m == ModalidadCobroTarifa.POR_VIAJE:
        total = b
        desc = f"POR_VIAJE: tarifa fija base {b} (sin km/peso/tiempo en linea)"
        return total, desc
    if m == ModalidadCobroTarifa.POR_TONELADA:
        total = b + (tarifa.tarifa_kg * peso_kg) + (tarifa.tarifa_tonelada * toneladas)
        desc = (
            f"POR_TONELADA: base {b} + kg({peso_kg}×{tarifa.tarifa_kg}) + "
            f"ton({toneladas}×{tarifa.tarifa_tonelada})"
        )
        return total, desc
    if m == ModalidadCobroTarifa.POR_HORA:
        total = b + (tarifa.tarifa_hora * horas_servicio)
        desc = f"POR_HORA: base {b} + horas({horas_servicio}×{tarifa.tarifa_hora})"
        return total, desc
    if m == ModalidadCobroTarifa.POR_DIA:
        total = b + (tarifa.tarifa_dia * dias_servicio)
        desc = f"POR_DIA: base {b} + dias({dias_servicio}×{tarifa.tarifa_dia})"
        return total, desc
    # fallback defensivo
    total = (
        b
        + (tarifa.tarifa_km * distancia_km)
        + (tarifa.tarifa_kg * peso_kg)
        + (tarifa.tarifa_tonelada * toneladas)
        + (tarifa.tarifa_hora * horas_servicio)
        + (tarifa.tarifa_dia * dias_servicio)
    )
    return total, f"MIXTA (fallback): linea compuesta = {total}"


def advertencias_auditoria_tarifa(
    tarifa: _TarifaLinea,
    *,
    distancia_km: Decimal,
    peso_kg: Decimal,
    horas_servicio: Decimal,
    dias_servicio: Decimal,
) -> list[str]:
    """Alertas para evitar doble cobro o tarifas mal configuradas."""
    adv: list[str] = []
    m = tarifa.modalidad_cobro

    if m == ModalidadCobroTarifa.MIXTA:
        if tarifa.tarifa_kg > 0 and tarifa.tarifa_tonelada > 0:
            adv.append(
                "MIXTA: activos tarifa_kg y tarifa_tonelada; confirma que el doble componente "
                "de peso es intencional (evita duplicar el mismo concepto)."
            )
    elif m == ModalidadCobroTarifa.POR_KM:
        if tarifa.tarifa_km <= 0:
            adv.append("POR_KM: tarifa_km es cero; revisa el catalogo o usa otra modalidad.")
    elif m == ModalidadCobroTarifa.POR_TONELADA:
        if tarifa.tarifa_kg <= 0 and tarifa.tarifa_tonelada <= 0:
            adv.append(
                "POR_TONELADA: sin coeficiente de peso (tarifa_kg/tarifa_tonelada); "
                "solo aplicara la base."
            )
    elif m == ModalidadCobroTarifa.POR_HORA:
        if horas_servicio > 0 and tarifa.tarifa_hora <= 0:
            adv.append("POR_HORA: hay horas de servicio pero tarifa_hora es cero.")
    elif m == ModalidadCobroTarifa.POR_DIA:
        if dias_servicio > 0 and tarifa.tarifa_dia <= 0:
            adv.append("POR_DIA: hay dias de servicio pero tarifa_dia es cero.")
    elif m == ModalidadCobroTarifa.POR_VIAJE:
        if distancia_km > 0 and tarifa.tarifa_km > 0:
            adv.append(
                "POR_VIAJE: hay km en el servicio y la tarifa tiene tarifa_km>0; "
                "esos km no entran en la linea (solo base). Usa POR_KM o MIXTA si cobras por km."
            )

    return adv
