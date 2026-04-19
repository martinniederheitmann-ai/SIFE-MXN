"""Sugerencia de asignación usando transportistas + tarifas de compra."""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy.orm import Session

from app.crud import transportista as crud_tr
from app.models.transportista import NivelConfianzaTransportista
from app.schemas.flete import FleteCompraCotizacionRequest
from app.schemas.motor_tarifa import (
    AsignacionSugeridaEntrada,
    AsignacionSugeridaResultado,
    CandidatoAsignacion,
    CandidatoAsignacionDetalle,
    MotorAsignacionEntrada,
)
from app.services.cotizacion_compra import cotizar_compra_con_tarifa
from app.services.motor_tarifas import ejecutar_asignacion


def _confianza_a_decimal(nivel: NivelConfianzaTransportista | None) -> Decimal:
    if nivel == NivelConfianzaTransportista.ALTO:
        return Decimal("4.5")
    if nivel == NivelConfianzaTransportista.MEDIO:
        return Decimal("3")
    return Decimal("2")


def asignacion_sugerida_desde_catalogo(
    db: Session, payload: AsignacionSugeridaEntrada
) -> AsignacionSugeridaResultado:
    transportistas, _ = crud_tr.list_transportistas(
        db, skip=0, limit=payload.limite_candidatos, activo=payload.solo_activos
    )

    detalles: list[CandidatoAsignacionDetalle] = []
    candidatos_motor: list[CandidatoAsignacion] = []
    peso_kg = (payload.toneladas * Decimal("1000")).quantize(Decimal("0.001"))

    for tr in transportistas:
        req = FleteCompraCotizacionRequest(
            transportista_id=tr.id,
            ambito=payload.ambito,
            origen=payload.origen,
            destino=payload.destino,
            tipo_unidad=payload.tipo_unidad,
            tipo_carga=payload.tipo_carga,
            distancia_km=payload.km,
            peso_kg=peso_kg,
        )
        try:
            cot = cotizar_compra_con_tarifa(db, req)
        except ValueError:
            continue

        costo = cot.costo_compra_sugerido
        tarifa_venta = (costo * payload.factor_sobre_costo).quantize(Decimal("0.01"))
        ganancia = (tarifa_venta - costo).quantize(Decimal("0.01"))
        conf = _confianza_a_decimal(tr.nivel_confianza)

        detalles.append(
            CandidatoAsignacionDetalle(
                transportista_id=tr.id,
                nombre=tr.nombre,
                tipo_transportista=tr.tipo_transportista.value,
                costo_compra=costo,
                tarifa_venta_sugerida=tarifa_venta,
                ganancia=ganancia,
                nivel_confianza=conf,
                tarifa_compra_id=cot.tarifa_id,
                detalle=cot.detalle_calculo,
            )
        )
        candidatos_motor.append(
            CandidatoAsignacion(
                transportista_id=tr.id,
                tipo=tr.tipo_transportista,
                costo_estimado=costo,
                tarifa_venta=tarifa_venta,
                ganancia=ganancia,
                nivel_confianza=conf,
            )
        )

    if not candidatos_motor:
        ranking = ejecutar_asignacion(MotorAsignacionEntrada(candidatos=[]))
        return AsignacionSugeridaResultado(candidatos=[], ranking=ranking)

    ranking = ejecutar_asignacion(MotorAsignacionEntrada(candidatos=candidatos_motor))
    return AsignacionSugeridaResultado(candidatos=detalles, ranking=ranking)
