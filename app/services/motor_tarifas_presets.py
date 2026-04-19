"""Aplicar presets de zona (BD) al motor de tarifas."""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy.orm import Session

from app.crud import motor_tarifa_zona as crud_zona
from app.models.tarifa_flete import AmbitoTarifaFlete
from app.schemas.motor_tarifa import MotorTarifaEntrada, NivelZonaMX


def normalizar_tipo_unidad_preset(tipo_unidad: str) -> str:
    u = tipo_unidad.strip().lower()
    if u in {"trailer", "tráiler", "full"}:
        return "tractocamion"
    return u


def enriquecer_desde_presets_bd(db: Session, entrada: MotorTarifaEntrada) -> MotorTarifaEntrada:
    region = entrada.nivel_zona.value
    tipo_u = normalizar_tipo_unidad_preset(entrada.tipo_unidad)
    preset = crud_zona.get_preset(db, region_key=region, tipo_unidad_norm=tipo_u)
    if preset is None and region != NivelZonaMX.GENERICA.value:
        preset = crud_zona.get_preset(db, region_key="generica", tipo_unidad_norm=tipo_u)
    if preset is None:
        return entrada

    updates: dict = {}
    if entrada.cpk_variable is None:
        updates["cpk_variable"] = preset.cpk_referencia

    ambito = entrada.ambito
    if ambito == AmbitoTarifaFlete.LOCAL and preset.mu_local is not None:
        updates["mu_local"] = preset.mu_local
    elif ambito == AmbitoTarifaFlete.ESTATAL and preset.mu_estatal is not None:
        updates["mu_estatal"] = preset.mu_estatal
    elif ambito == AmbitoTarifaFlete.FEDERAL and preset.mu_federal is not None:
        updates["mu_federal"] = preset.mu_federal

    if not updates:
        return entrada
    return entrada.model_copy(update=updates)
