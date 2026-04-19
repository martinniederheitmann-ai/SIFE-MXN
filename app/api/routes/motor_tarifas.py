"""API del motor de tarifas (costos + tipos de operación + asignación)."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.crud import motor_tarifa_zona as crud_zona
from app.schemas.motor_tarifa import (
    AsignacionSugeridaEntrada,
    AsignacionSugeridaResultado,
    MotorAsignacionEntrada,
    MotorAsignacionResultado,
    MotorTarifaEntrada,
    MotorTarifaResultado,
    MotorTarifaZonaPresetRead,
)
from app.services.motor_tarifas import ejecutar_asignacion, ejecutar_motor
from app.services.motor_tarifas_catalogo import asignacion_sugerida_desde_catalogo
from app.services.motor_tarifas_presets import enriquecer_desde_presets_bd

router = APIRouter()


@router.post(
    "/cotizar",
    response_model=MotorTarifaResultado,
    summary="Motor de tarifas (propio, subcontratado, fletero, aliado, híbrido MAX)",
)
def motor_cotizar(
    payload: MotorTarifaEntrada,
    db: Session = Depends(get_db),
    usar_presets_bd: bool = Query(
        False,
        description="Si true, rellena CPK y MU desde motor_tarifa_zona_presets (región + tipo unidad).",
    ),
) -> MotorTarifaResultado:
    entrada = enriquecer_desde_presets_bd(db, payload) if usar_presets_bd else payload
    try:
        return ejecutar_motor(entrada)
    except ValueError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e)) from e


@router.post(
    "/asignacion",
    response_model=MotorAsignacionResultado,
    summary="Ranking de transportistas por score (ganancia, confianza, distancia, tiempo)",
)
def motor_asignacion(payload: MotorAsignacionEntrada) -> MotorAsignacionResultado:
    if not payload.candidatos:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Debe enviar al menos un candidato con disponibilidad.",
        )
    return ejecutar_asignacion(payload)


@router.post(
    "/asignacion-sugerida",
    response_model=AsignacionSugeridaResultado,
    summary="Ranking usando tarifas de compra activas (origen/destino/unidad) por transportista",
)
def motor_asignacion_sugerida(
    payload: AsignacionSugeridaEntrada,
    db: Session = Depends(get_db),
) -> AsignacionSugeridaResultado:
    return asignacion_sugerida_desde_catalogo(db, payload)


@router.get(
    "/presets-zona",
    response_model=list[MotorTarifaZonaPresetRead],
    summary="Presets de mercado (CPK/MU) por región y tipo de unidad",
)
def list_presets_zona(
    db: Session = Depends(get_db),
    activo: bool | None = True,
) -> list[MotorTarifaZonaPresetRead]:
    rows = crud_zona.list_presets(db, activo=activo)
    return list(rows)
